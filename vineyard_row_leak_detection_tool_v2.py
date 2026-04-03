# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterDefinition,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsWkbTypes,
    QgsVectorLayer,
    QgsProject,
)
import processing
import math


class VineyardRowLeakDetectionToolV2(QgsProcessingAlgorithm):
    ROWS = "ROWS"
    THERMAL = "THERMAL"
    VEG_MASK = "VEG_MASK"

    USE_BLOCK = "USE_BLOCK"
    BLOCKS = "BLOCKS"

    SECTION_LENGTH = "SECTION_LENGTH"
    ROW_BUFFER = "ROW_BUFFER"
    MIN_SECTION_LENGTH = "MIN_SECTION_LENGTH"
    MIN_BLOCK_INTERSECTION = "MIN_BLOCK_INTERSECTION"

    SAVE_NONVINE = "SAVE_NONVINE"
    OUTPUT_NONVINE = "OUTPUT_NONVINE"
    OUTPUT_ROWS = "OUTPUT_ROWS"

    NODATA_VALUE = -9999.0

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return VineyardRowLeakDetectionToolV2()

    def name(self):
        return "vineyard_row_leak_detection_tool_v2"

    def displayName(self):
        return self.tr("Vineyard Row Leak Detection Tool v2")

    def group(self):
        return self.tr("Viticulture")

    def groupId(self):
        return "viticulture"

    def shortHelpString(self):
        return self.tr(
            "Segmented row-section vineyard leak screening using aligned thermal and a binary vegetation mask. "
            "This v2 tool splits rows into equal-length sections before buffering and scoring."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.ROWS, self.tr("Row centerlines"), [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterRasterLayer(self.THERMAL, self.tr("Aligned thermal raster")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.VEG_MASK, self.tr("Binary vegetation mask raster (1 vegetation, 0 non-vegetation)")))
        self.addParameter(QgsProcessingParameterBoolean(self.USE_BLOCK, self.tr("Use block polygon to retain sections with sufficient intersection"), defaultValue=False))

        block_param = QgsProcessingParameterFeatureSource(self.BLOCKS, self.tr("Block polygon (optional)"), [QgsProcessing.TypeVectorPolygon], optional=True)
        block_param.setFlags(block_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(block_param)

        self.addParameter(QgsProcessingParameterNumber(self.SECTION_LENGTH, self.tr("Target row section length (m)"), type=QgsProcessingParameterNumber.Double, defaultValue=2.0, minValue=0.1))
        self.addParameter(QgsProcessingParameterNumber(self.ROW_BUFFER, self.tr("Row section buffer distance (m)"), type=QgsProcessingParameterNumber.Double, defaultValue=0.5, minValue=0.01))
        self.addParameter(QgsProcessingParameterNumber(self.MIN_SECTION_LENGTH, self.tr("Minimum retained section length (m)"), type=QgsProcessingParameterNumber.Double, defaultValue=1.0, minValue=0.0))

        min_block_param = QgsProcessingParameterNumber(self.MIN_BLOCK_INTERSECTION, self.tr("Minimum section length intersecting block polygon (m)"), type=QgsProcessingParameterNumber.Double, defaultValue=1.0, minValue=0.0)
        min_block_param.setFlags(min_block_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(min_block_param)

        self.addParameter(QgsProcessingParameterBoolean(self.SAVE_NONVINE, self.tr("Save derived non-vine thermal raster"), defaultValue=False))

        out_nonvine_param = QgsProcessingParameterRasterDestination(self.OUTPUT_NONVINE, self.tr("Output non-vine thermal raster"), optional=True)
        out_nonvine_param.setFlags(out_nonvine_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(out_nonvine_param)

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_ROWS, self.tr("Output row-section leak screening layer")))

    def _quantile(self, values, q):
        vals = sorted([float(v) for v in values if v is not None and math.isfinite(float(v))])
        if not vals:
            return None
        pos = (len(vals) - 1) * q
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return vals[lo]
        return vals[lo] * (hi - pos) + vals[hi] * (pos - lo)

    def _safe_float(self, value):
        if value is None:
            return None
        try:
            v = float(value)
        except Exception:
            return None
        if not math.isfinite(v):
            return None
        return v

    def _pick_result_value(self, result_dict, preferred_keys):
        for key in preferred_keys:
            if key in result_dict and result_dict[key] is not None:
                return result_dict[key]
        raise QgsProcessingException(f"Could not find expected output key in processing result. Available keys: {list(result_dict.keys())}")

    def _resolve_vector_layer(self, obj, fallback_name="resolved_layer"):
        if hasattr(obj, "getFeatures") and hasattr(obj, "fields"):
            return obj
        if isinstance(obj, str):
            layers = QgsProject.instance().mapLayersByName(obj)
            if layers:
                return layers[0]
            lyr = QgsVectorLayer(obj, fallback_name, "ogr")
            if lyr.isValid():
                return lyr
        raise QgsProcessingException(f"Could not resolve vector layer from result object: {repr(obj)}")

    def processAlgorithm(self, parameters, context, feedback):
        rows = self.parameterAsSource(parameters, self.ROWS, context)
        thermal = self.parameterAsRasterLayer(parameters, self.THERMAL, context)
        veg_mask = self.parameterAsRasterLayer(parameters, self.VEG_MASK, context)
        use_block = self.parameterAsBoolean(parameters, self.USE_BLOCK, context)
        blocks = self.parameterAsSource(parameters, self.BLOCKS, context)

        section_length = self.parameterAsDouble(parameters, self.SECTION_LENGTH, context)
        row_buffer = self.parameterAsDouble(parameters, self.ROW_BUFFER, context)
        min_section_length = self.parameterAsDouble(parameters, self.MIN_SECTION_LENGTH, context)
        min_block_intersection = self.parameterAsDouble(parameters, self.MIN_BLOCK_INTERSECTION, context)

        save_nonvine = self.parameterAsBoolean(parameters, self.SAVE_NONVINE, context)
        output_nonvine = self.parameterAsOutputLayer(parameters, self.OUTPUT_NONVINE, context)

        if rows is None:
            raise QgsProcessingException("Row layer is invalid.")
        if thermal is None:
            raise QgsProcessingException("Thermal raster is invalid.")
        if veg_mask is None:
            raise QgsProcessingException("Vegetation mask raster is invalid.")
        if use_block and blocks is None:
            raise QgsProcessingException("Use block is checked, but no block polygon was provided.")
        if save_nonvine and not output_nonvine:
            raise QgsProcessingException("Save derived non-vine thermal raster is checked, but no output raster path was provided.")

        feedback.pushInfo("Aligning vegetation mask to thermal raster grid...")
        xres = thermal.rasterUnitsPerPixelX()
        extent = thermal.extent()
        thermal_crs = thermal.crs().authid()

        mask_result = processing.run(
            "gdal:warpreproject",
            {
                "INPUT": veg_mask,
                "SOURCE_CRS": None,
                "TARGET_CRS": thermal.crs(),
                "RESAMPLING": 0,
                "NODATA": None,
                "TARGET_RESOLUTION": abs(xres),
                "OPTIONS": "",
                "DATA_TYPE": 5,
                "TARGET_EXTENT": f"{extent.xMinimum()},{extent.xMaximum()},{extent.yMinimum()},{extent.yMaximum()} [{thermal_crs}]",
                "TARGET_EXTENT_CRS": thermal.crs(),
                "MULTITHREADING": False,
                "EXTRA": "",
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
            context=context,
            feedback=feedback,
        )
        matched_mask = self._pick_result_value(mask_result, ["OUTPUT"])

        feedback.pushInfo("Creating non-vine thermal raster...")
        nonvine_output = output_nonvine if save_nonvine else "TEMPORARY_OUTPUT"
        nonvine_result = processing.run(
            "gdal:rastercalculator",
            {
                "INPUT_A": thermal,
                "BAND_A": 1,
                "INPUT_B": matched_mask,
                "BAND_B": 1,
                "FORMULA": f"(B<=0.5)*A + (B>0.5)*({self.NODATA_VALUE})",
                "NO_DATA": self.NODATA_VALUE,
                "RTYPE": 5,
                "OPTIONS": "",
                "EXTRA": "",
                "OUTPUT": nonvine_output,
            },
            context=context,
            feedback=feedback,
        )
        nonvine_raster = self._pick_result_value(nonvine_result, ["OUTPUT"])

        feedback.pushInfo("Preparing working row layer...")
        working_rows_result = processing.run("native:multiparttosingleparts", {"INPUT": parameters[self.ROWS], "OUTPUT": "memory:"}, context=context, feedback=feedback)
        working_rows = self._resolve_vector_layer(self._pick_result_value(working_rows_result, ["OUTPUT"]), "working_rows")

        feedback.pushInfo("Splitting rows into equal-length sections...")
        split_result = processing.run("native:splitlinesbylength", {"INPUT": working_rows, "LENGTH": section_length, "OUTPUT": "memory:"}, context=context, feedback=feedback)
        sections = self._resolve_vector_layer(self._pick_result_value(split_result, ["OUTPUT"]), "sections")

        field_names = [fld.name() for fld in sections.fields()]
        if "seg_len_m" not in field_names:
            fc_result = processing.run("native:fieldcalculator", {"INPUT": sections, "FIELD_NAME": "seg_len_m", "FIELD_TYPE": 0, "FIELD_LENGTH": 20, "FIELD_PRECISION": 3, "FORMULA": "$length", "OUTPUT": "memory:"}, context=context, feedback=feedback)
            sections = self._resolve_vector_layer(self._pick_result_value(fc_result, ["OUTPUT"]), "sections_len")

        sections_filtered_result = processing.run("native:extractbyexpression", {"INPUT": sections, "EXPRESSION": f'coalesce("seg_len_m", $length) >= {min_section_length}', "OUTPUT": "memory:"}, context=context, feedback=feedback)
        sections_filtered = self._resolve_vector_layer(self._pick_result_value(sections_filtered_result, ["OUTPUT"]), "sections_filtered")

        if use_block:
            feedback.pushInfo("Measuring section-block intersection lengths...")
            section_block_result = processing.run("native:intersection", {"INPUT": sections_filtered, "OVERLAY": parameters[self.BLOCKS], "INPUT_FIELDS": [], "OVERLAY_FIELDS": [], "OVERLAY_FIELDS_PREFIX": "", "OUTPUT": "memory:"}, context=context, feedback=feedback)
            section_block = self._resolve_vector_layer(self._pick_result_value(section_block_result, ["OUTPUT"]), "section_block")
            section_block_fc = processing.run("native:fieldcalculator", {"INPUT": section_block, "FIELD_NAME": "blk_len_m", "FIELD_TYPE": 0, "FIELD_LENGTH": 20, "FIELD_PRECISION": 3, "FORMULA": "$length", "OUTPUT": "memory:"}, context=context, feedback=feedback)
            section_block = self._resolve_vector_layer(self._pick_result_value(section_block_fc, ["OUTPUT"]), "section_block_fc")
            join_result = processing.run("native:joinattributesbylocationsummary", {"INPUT": sections_filtered, "JOIN": section_block, "PREDICATE": [0], "JOIN_FIELDS": ["blk_len_m"], "SUMMARIES": [5], "DISCARD_NONMATCHING": False, "OUTPUT": "memory:"}, context=context, feedback=feedback)
            sections_filtered = self._resolve_vector_layer(self._pick_result_value(join_result, ["OUTPUT"]), "sections_joined")
            extract_result = processing.run("native:extractbyexpression", {"INPUT": sections_filtered, "EXPRESSION": f'coalesce("blk_len_m_sum", 0) >= {min_block_intersection}', "OUTPUT": "memory:"}, context=context, feedback=feedback)
            sections_filtered = self._resolve_vector_layer(self._pick_result_value(extract_result, ["OUTPUT"]), "sections_block_filtered")

        feedback.pushInfo("Adding section IDs...")
        add_seg_result = processing.run("native:fieldcalculator", {"INPUT": sections_filtered, "FIELD_NAME": "seg_id", "FIELD_TYPE": 1, "FIELD_LENGTH": 20, "FIELD_PRECISION": 0, "FORMULA": "$id", "OUTPUT": "memory:"}, context=context, feedback=feedback)
        sections_filtered = self._resolve_vector_layer(self._pick_result_value(add_seg_result, ["OUTPUT"]), "sections_with_seg_id")

        feedback.pushInfo("Buffering row sections...")
        buffer_result = processing.run("native:buffer", {"INPUT": sections_filtered, "DISTANCE": row_buffer, "SEGMENTS": 8, "END_CAP_STYLE": 0, "JOIN_STYLE": 0, "MITER_LIMIT": 2, "DISSOLVE": False, "OUTPUT": "memory:"}, context=context, feedback=feedback)
        section_buffered = self._resolve_vector_layer(self._pick_result_value(buffer_result, ["OUTPUT"]), "section_buffered")
        multi_result = processing.run("native:multiparttosingleparts", {"INPUT": section_buffered, "OUTPUT": "memory:"}, context=context, feedback=feedback)
        section_buffered = self._resolve_vector_layer(self._pick_result_value(multi_result, ["OUTPUT"]), "section_buffered_single")

        feedback.pushInfo("Calculating zonal mean non-vine temperatures by section...")
        processing.run("native:zonalstatistics", {"INPUT_RASTER": nonvine_raster, "RASTER_BAND": 1, "INPUT_VECTOR": section_buffered, "COLUMN_PREFIX": "nz_", "STATISTICS": [2]}, context=context, feedback=feedback)
        zstats = section_buffered

        features = list(zstats.getFeatures())
        if not features:
            raise QgsProcessingException("No buffered row-section features were available for analysis.")

        z_field_names = [f.name() for f in zstats.fields()]
        if "nz_mean" not in z_field_names:
            raise QgsProcessingException(f"Zonal statistics did not produce nz_mean. Available fields: {z_field_names}")

        valid_means = []
        for f in features:
            mv = self._safe_float(f["nz_mean"])
            if mv is None or mv == self.NODATA_VALUE:
                continue
            valid_means.append(mv)

        if not valid_means:
            raise QgsProcessingException("No valid mean temperatures were calculated. Check thermal alignment, vegetation mask, section length, and buffer distance.")

        q20 = self._quantile(valid_means, 0.20)
        if q20 is None:
            raise QgsProcessingException("Could not compute q20 from section mean temperatures.")

        mean_all = sum(valid_means) / len(valid_means)
        sorted_means = sorted(valid_means)

        feedback.pushInfo(f"Computed section-temperature q20 threshold: {q20:.4f}")
        feedback.pushInfo(f"Computed section-temperature mean: {mean_all:.4f}")

        def cool_rank(value):
            v = self._safe_float(value)
            if v is None:
                return None
            for i, sv in enumerate(sorted_means):
                if v <= sv:
                    return i + 1
            return len(sorted_means)

        out_fields = QgsFields()
        for fld in zstats.fields():
            out_fields.append(fld)
        for fld in [QgsField("q20", QVariant.Double), QgsField("field_mean", QVariant.Double), QgsField("delta_mean", QVariant.Double), QgsField("flag", QVariant.Int), QgsField("rank_cool", QVariant.Int), QgsField("pct_rank", QVariant.Double)]:
            if out_fields.indexOf(fld.name()) == -1:
                out_fields.append(fld)

        sink, dest_id = self.parameterAsSink(parameters, self.OUTPUT_ROWS, context, out_fields, QgsWkbTypes.Polygon, rows.sourceCrs())

        kept = 0
        n_valid = len(sorted_means)
        for f in features:
            geom = f.geometry()
            if geom is None or geom.isEmpty():
                continue
            mean_val = self._safe_float(f["nz_mean"])
            if mean_val is None or mean_val == self.NODATA_VALUE:
                continue
            out_feat = QgsFeature(out_fields)
            out_feat.setGeometry(geom)
            for fld in zstats.fields():
                try:
                    out_feat[fld.name()] = f[fld.name()]
                except Exception:
                    pass
            rank_val = cool_rank(mean_val)
            pct_rank = (float(rank_val) / float(n_valid)) if rank_val is not None and n_valid > 0 else None
            out_feat["q20"] = float(q20)
            out_feat["field_mean"] = float(mean_all)
            out_feat["delta_mean"] = float(mean_val - mean_all)
            out_feat["flag"] = 1 if mean_val <= q20 else 0
            out_feat["rank_cool"] = int(rank_val) if rank_val is not None else None
            out_feat["pct_rank"] = float(pct_rank) if pct_rank is not None else None
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)
            kept += 1

        if kept == 0:
            raise QgsProcessingException("No output row sections were written. Check section geometry, buffers, and thermal/mask overlap.")

        results = {self.OUTPUT_ROWS: dest_id}
        if save_nonvine:
            results[self.OUTPUT_NONVINE] = nonvine_raster
        return results
