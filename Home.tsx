import { Button } from "@/components/ui/button";
import { ChevronRight, Droplets, Leaf, MapPin, Zap } from "lucide-react";
import { useState } from "react";

/**
 * AeroSpect - Minimalist Design
 * 
 * Design Philosophy: Clean, spacious, modern
 * - Light backgrounds with generous whitespace
 * - Blue (#00B4E6) as primary accent color
 * - Soft decorative circles for visual interest
 * - Clear section hierarchy
 * - Minimal borders and shadows
 * - Focus on content and clarity
 */

export default function Home() {
  const [selectedSeason, setSelectedSeason] = useState("winter");

  const seasons = {
    winter: {
      title: "Winter (Dec – Feb)",
      focus: "Pruning, Tying & Site Preparation",
      sensors: [
        {
          name: "RGB (High-Resolution)",
          description:
            "Clear visual representation of vineyard structure without canopy obstruction. Precise mapping of trellis systems and identification of broken posts or wires.",
        },
        {
          name: "Multispectral",
          description:
            "Analyzes cover crop establishment and vigor, ensuring soil health is maintained during the dormant season.",
        },
        {
          name: "Thermal",
          description:
            "Identifies drainage issues or soil moisture pooling, critical for planning erosion control or regrading.",
        },
      ],
    },
    spring: {
      title: "Spring (Mar – May)",
      focus: "Canopy Management, Nutrients & Frost Protection",
      sensors: [
        {
          name: "Multispectral",
          description:
            "Essential for early-season vigor mapping. Identifies hot spots or weak zones to guide precise nutrient application.",
        },
        {
          name: "Thermal",
          description:
            "Highly effective for frost protection. Monitors temperature inversions and tracks efficiency of wind fans or sprinklers in real-time.",
        },
        {
          name: "RGB",
          description:
            "Detailed scouting of early pest and disease outbreaks, creating high-resolution digital maps for targeted sprays.",
        },
      ],
    },
    summer: {
      title: "Summer (Jun – Aug)",
      focus: "Irrigation, Veraison & Canopy Thinning",
      sensors: [
        {
          name: "Thermal",
          description:
            "Primary tool for irrigation management. Detects water stress in individual vines before visible wilting occurs.",
        },
        {
          name: "Multispectral",
          description:
            "Tracks uniformity of veraison. Monitors leaf color and canopy health to identify sections ripening at different rates.",
        },
        {
          name: "RGB",
          description:
            "Facilitates canopy management by providing vigor maps that highlight where leaf removal or thinning is required.",
        },
      ],
    },
    fall: {
      title: "Fall (Sep – Nov)",
      focus: "Harvest & Erosion Control",
      sensors: [
        {
          name: "Multispectral & RGB",
          description:
            "Create selective harvest maps. Identify areas with consistent sugar/acid levels for peak quality picking.",
        },
        {
          name: "Thermal",
          description:
            "Monitors soil moisture to ensure ground stability for heavy harvest equipment, preventing soil compaction.",
        },
        {
          name: "Digital Analysis",
          description:
            "Post-harvest high-resolution maps used to plan erosion control and cover crop seeding for the upcoming winter.",
        },
      ],
    },
  };

  const currentSeason = seasons[selectedSeason as keyof typeof seasons];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 z-50">
        <div className="container flex items-center justify-between h-16">
          <img
            src="/aerospect-logo.png"
            alt="AeroSpect"
            className="h-14 w-auto"
          />
          <div className="hidden md:flex items-center gap-8">
            <a
              href="#approach"
              className="text-sm text-gray-600 hover:text-blue-600 transition"
            >
              Our Approach
            </a>
            <a
              href="#seasons"
              className="text-sm text-gray-600 hover:text-blue-600 transition"
            >
              Year-Round Services
            </a>
            <a
              href="#services"
              className="text-sm text-gray-600 hover:text-blue-600 transition"
            >
              Services
            </a>
            <a
              href="#contact"
              className="text-sm text-gray-600 hover:text-blue-600 transition"
            >
              Contact
            </a>
          </div>
          <Button
            className="bg-blue-600 hover:bg-blue-700 text-white"
            size="sm"
          >
            Get Assessment
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-24 px-4 relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute top-20 right-10 w-32 h-32 bg-blue-100 rounded-full opacity-40 blur-2xl" />
        <div className="absolute bottom-0 left-10 w-40 h-40 bg-cyan-100 rounded-full opacity-30 blur-2xl" />

        <div className="container max-w-3xl mx-auto text-center relative z-10">
          <div className="inline-block px-4 py-2 bg-blue-50 rounded-full border border-blue-200 mb-6">
            <span className="text-sm font-medium text-blue-600">
              Precision Viticulture
            </span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Elevate Your Vineyard with Aerial Intelligence
          </h1>

          <p className="text-xl text-gray-600 mb-10 leading-relaxed">
            Drone-powered insights that transform vineyard management. Make
            smarter decisions, improve grape quality, and maximize yields.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
            >
              Free Assessment <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 rounded-lg"
            >
              Year-Round Services
            </Button>
          </div>
        </div>
      </section>

      {/* Approach Section */}
      <section id="approach" className="py-24 px-4 bg-gray-50">
        <div className="container max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Data-Driven Vineyard Excellence
            </h2>
            <p className="text-lg text-gray-600">
              Drone imagery utilizing RGB, thermal, and multispectral sensors
              provides actionable data throughout the entire vineyard lifecycle.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: MapPin,
                title: "Unmatched Precision",
                description:
                  "High-resolution cameras and multispectral sensors monitor every aspect of your vineyard with unprecedented accuracy.",
              },
              {
                icon: Leaf,
                title: "Sustainable Practices",
                description:
                  "Optimize water usage, reduce chemical inputs, and promote sustainable farming through targeted interventions.",
              },
              {
                icon: Zap,
                title: "AI-Powered Insights",
                description:
                  "Advanced algorithms automatically detect and diagnose issues like pests and diseases before they become serious.",
              },
            ].map((item, idx) => (
              <div
                key={idx}
                className="p-6 bg-white rounded-lg border border-gray-200 hover:shadow-lg transition"
              >
                <item.icon className="h-8 w-8 text-blue-600 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Seasonal Services Section */}
      <section id="seasons" className="py-24 px-4 relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute top-40 left-5 w-36 h-36 bg-blue-100 rounded-full opacity-20 blur-2xl" />
        <div className="absolute bottom-20 right-10 w-44 h-44 bg-cyan-100 rounded-full opacity-15 blur-2xl" />

        <div className="container max-w-4xl relative z-10">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Services for Every Season
            </h2>
            <p className="text-lg text-gray-600">
              Tailored drone solutions for each phase of the vineyard lifecycle
            </p>
          </div>

          {/* Season Selector */}
          <div className="flex flex-wrap gap-3 justify-center mb-12">
            {Object.entries(seasons).map(([key, season]) => (
              <button
                key={key}
                onClick={() => setSelectedSeason(key)}
                className={`px-6 py-3 rounded-lg font-medium transition ${
                  selectedSeason === key
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {season.title.split(" ")[0]}
              </button>
            ))}
          </div>

          {/* Season Details */}
          <div className="bg-white rounded-lg border border-gray-200 p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {currentSeason.title}
            </h3>
            <p className="text-blue-600 font-semibold mb-8">
              Focus: {currentSeason.focus}
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              {currentSeason.sensors.map((sensor, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {sensor.name}
                  </h4>
                  <p className="text-sm text-gray-600">{sensor.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-24 px-4 bg-gray-50">
        <div className="container max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Our Services
            </h2>
            <p className="text-lg text-gray-600">
              From routine inspections to advanced 3D modeling, tailored to
              your needs
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                title: "Mapping & Surveying",
                description:
                  "Accurate topographic mapping to guide vineyard layout, irrigation planning, and infrastructure development with centimeter-level precision.",
                feature: "Orthomosaics & 3D Models",
              },
              {
                title: "Inspections & Monitoring",
                description:
                  "Regular drone-based inspections to monitor vine health, detect diseases early, and ensure optimal growing conditions throughout the season.",
                feature: "Learn More →",
              },
              {
                title: "Thermal & Multispectral Imaging",
                description:
                  "Monitor soil moisture, identify drainage issues, and detect plant stress invisible to the naked eye with advanced sensor technology.",
                feature: "Advanced Analysis",
              },
              {
                title: "Custom Analysis",
                description:
                  "Tailored drone solutions for your specific vineyard challenges, from frost protection to selective harvest planning.",
                feature: "Personalized Quote",
              },
            ].map((service, idx) => (
              <div
                key={idx}
                className="p-8 bg-white rounded-lg border border-gray-200 hover:shadow-lg transition"
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {service.title}
                </h3>
                <p className="text-gray-600 mb-4">{service.description}</p>
                <a
                  href="#contact"
                  className="text-blue-600 font-medium hover:text-blue-700 transition"
                >
                  {service.feature} →
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-24 px-4 relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute top-10 right-5 w-32 h-32 bg-blue-100 rounded-full opacity-30 blur-2xl" />
        <div className="absolute bottom-10 left-10 w-40 h-40 bg-cyan-100 rounded-full opacity-20 blur-2xl" />

        <div className="container max-w-3xl text-center relative z-10">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Ready to Elevate Your Vineyard?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Contact us today to discuss how AeroSpect can transform your
            vineyard management with precision aerial solutions.
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-8">
            <a
              href="tel:707-819-6961"
              className="flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition"
            >
              <span>📞</span> 707-819-6961
            </a>
            <a
              href="mailto:ethan@aerospectinc.com"
              className="flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition"
            >
              <span>✉️</span> ethan@aerospectinc.com
            </a>
          </div>

          <p className="text-sm text-gray-500">Wine Country, CA</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 px-4">
        <div className="container flex items-center justify-between">
        <img
          src="/aerospect-logo.png"
          alt="AeroSpect"
          className="h-12 w-auto invert"
        />
          <p className="text-sm text-gray-400">
            © 2025 AeroSpect Inc. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
