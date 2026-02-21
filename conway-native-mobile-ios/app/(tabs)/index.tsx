import React, { useMemo, useState } from "react";
import { View, Text, TextInput, Pressable, FlatList } from "react-native";
import * as api from "../../src/api";

export default function HomeScreen() {
  const [email, setEmail] = useState("ethan@example.com");
  const [userId, setUserId] = useState<string | null>(null);
  const [balance, setBalance] = useState<number>(0);
  const [birthTicket, setBirthTicket] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState("0xDEMO_WALLET");
  const [sandboxId, setSandboxId] = useState("demo_sandbox");
  const [agents, setAgents] = useState<any[]>([]);
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
  }

  async function buyCredits() {
    if (!userId) return;
    setErr(null);
    const r = await api.validateReceipt(email, 500); // $5
    setBalance(r.balanceCents);
  }

  async function birth() {
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

  async function register() {
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

  return (
    <View
      style={{
        flex: 1,
        padding: 16,
        marginTop: 48,
        backgroundColor: "#ffffff",
        gap: 12,
      }}
    >
      <Text style={{ fontSize: 22, fontWeight: "700" }}>Conway-Native Prototype</Text>

      {!userId ? (
        <View style={{ gap: 8 }}>
          <Text>Email</Text>
          <TextInput
            value={email}
            onChangeText={setEmail}
            style={{ borderWidth: 1, padding: 10, borderRadius: 10 }}
          />
          <Pressable onPress={doLogin} style={{ padding: 12, borderRadius: 12, borderWidth: 1 }}>
            <Text>Login</Text>
          </Pressable>
        </View>
      ) : (
        <>
          <Text>User: {userId}</Text>
          <Text>Balance: ${dollars}</Text>

          <View style={{ flexDirection: "row", gap: 10 }}>
            <Pressable onPress={buyCredits} style={{ padding: 12, borderRadius: 12, borderWidth: 1 }}>
              <Text>Buy $5 Credits (Mock)</Text>
            </Pressable>
            <Pressable onPress={birth} style={{ padding: 12, borderRadius: 12, borderWidth: 1 }}>
              <Text>Birth Agent ($2)</Text>
            </Pressable>
          </View>

          {birthTicket && (
            <View style={{ gap: 8, padding: 12, borderRadius: 12, borderWidth: 1 }}>
              <Text style={{ fontWeight: "700" }}>Register newborn</Text>
              <TextInput
                value={walletAddress}
                onChangeText={setWalletAddress}
                style={{ borderWidth: 1, padding: 10, borderRadius: 10 }}
              />
              <TextInput
                value={sandboxId}
                onChangeText={setSandboxId}
                style={{ borderWidth: 1, padding: 10, borderRadius: 10 }}
              />
              <Pressable onPress={register} style={{ padding: 12, borderRadius: 12, borderWidth: 1 }}>
                <Text>Register</Text>
              </Pressable>
            </View>
          )}

          {err && <Text style={{ color: "red" }}>{err}</Text>}

          <Text style={{ fontSize: 18, fontWeight: "700", marginTop: 12 }}>Agents</Text>
          <FlatList
            data={agents}
            keyExtractor={(x) => x.id}
            renderItem={({ item }) => (
              <View style={{ padding: 12, borderRadius: 12, borderWidth: 1, marginBottom: 10 }}>
                <Text style={{ fontWeight: "700" }}>{item.walletAddress}</Text>
                <Text>Status: {item.status}</Text>
                <Text>Sandbox: {item.sandboxId ?? "-"}</Text>
                <Text>Created: {new Date(item.createdAt).toLocaleString()}</Text>
              </View>
            )}
          />
        </>
      )}
    </View>
  );
}
