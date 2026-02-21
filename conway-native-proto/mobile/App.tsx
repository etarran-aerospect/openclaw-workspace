import React, { useMemo, useState } from "react";
import { View, Text, TextInput, Pressable, FlatList } from "react-native";
import * as api from "./src/api";

export default function App() {
  const [email, setEmail] = useState("ethan@example.com");
  const [userId, setUserId] = useState<string | null>(null);
  const [balance, setBalance] = useState<number>(0);
  const [birthTicket, setBirthTicket] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState("0xDEMO_WALLET");
  const [sandboxId, setSandboxId] = useState("demo_sandbox");
  const [agents, setAgents] = useState<any[]>([]);
  const [sandboxes, setSandboxes] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  const dollars = useMemo(() => (balance / 100).toFixed(2), [balance]);

  async function doLogin() {
    setErr(null);
    const r = await api.login(email);
    setUserId(r.userId);

    const b = await api.getBalance(r.userId);
    setBalance(b.balanceCents);

    const a = await api.listAgents(r.userId);
    setAgents(a.agents);

    try {
      const s = await api.listConwaySandboxes();
      setSandboxes(s.sandboxes);
    } catch (e: any) {
      setErr(e.message);
    }
  }

  async function buyCredits() {
    if (!userId) return;
    setErr(null);
    const r = await api.validateReceipt(email, 500); // $5
    setBalance(r.balanceCents);
  }

  async function birthDemoAgent() {
    if (!userId) return;
    setErr(null);
    try {
      const r = await api.birthAgent(userId, "template_basic");
      setBirthTicket(r.birthTicket);
      setBalance(r.balanceCents);
    } catch (e: any) {
      setErr(e.message);
    }
  }

  async function registerDemoAgent() {
    if (!birthTicket || !userId) return;
    setErr(null);
    try {
      await api.registerAgent(birthTicket, walletAddress, sandboxId);
      setBirthTicket(null);
      const a = await api.listAgents(userId);
      setAgents(a.agents);
    } catch (e: any) {
      setErr(e.message);
    }
  }

  async function birthConwaySandbox() {
    setErr(null);
    try {
      const name = "PDFAuton-1-mobile-" + Date.now().toString().slice(-4);
      await api.provisionConwaySandbox(name, "micro");
      const s = await api.listConwaySandboxes();
      setSandboxes(s.sandboxes);
    } catch (e: any) {
      setErr(e.message);
    }
  }

  return (
    <View style={{ flex: 1, backgroundColor: "#0b1020" }}>
      <View
        style={{
          marginTop: 60,
          marginHorizontal: 20,
          padding: 16,
          borderRadius: 20,
          backgroundColor: "#111827",
          shadowColor: "#000",
          shadowOpacity: 0.25,
          shadowRadius: 10,
          shadowOffset: { width: 0, height: 4 },
          elevation: 4,
        }}
      >
        <Text
          style={{
            fontSize: 24,
            fontWeight: "800",
            color: "#e5e7eb",
            marginBottom: 4,
          }}
        >
          Conway-Native
        </Text>
        <Text style={{ color: "#9ca3af", marginBottom: 16 }}>
          Birth, fund, and track Conway agents from your phone.
        </Text>

        {!userId ? (
          <>
            <Text style={{ color: "#d1d5db", marginBottom: 6 }}>Email</Text>
            <TextInput
              value={email}
              onChangeText={setEmail}
              placeholder="you@example.com"
              placeholderTextColor="#6b7280"
              autoCapitalize="none"
              keyboardType="email-address"
              style={{
                borderWidth: 1,
                borderColor: "#4b5563",
                backgroundColor: "#020617",
                color: "#e5e7eb",
                paddingHorizontal: 12,
                paddingVertical: 10,
                borderRadius: 10,
                marginBottom: 12,
              }}
            />
            <Pressable
              onPress={doLogin}
              style={({ pressed }) => ({
                backgroundColor: pressed ? "#4f46e5" : "#6366f1",
                paddingVertical: 12,
                borderRadius: 999,
                alignItems: "center",
                marginBottom: 8,
              })}
            >
              <Text style={{ color: "white", fontWeight: "600" }}>Login</Text>
            </Pressable>
          </>
        ) : (
          <>
            <View
              style={{
                padding: 12,
                borderRadius: 12,
                backgroundColor: "#020617",
                borderWidth: 1,
                borderColor: "#1f2937",
                marginBottom: 12,
              }}
            >
              <Text style={{ color: "#9ca3af", marginBottom: 4 }}>
                Logged in as
              </Text>
              <Text
                style={{ color: "#e5e7eb", fontSize: 12 }}
                numberOfLines={1}
              >
                {userId}
              </Text>
              <Text style={{ color: "#9ca3af", marginTop: 8 }}>
                Demo balance:{