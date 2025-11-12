/* app/score.tsx */

import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet, Alert } from "react-native";

export default function ScoreScreen() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const checkUrl = async () => {
    if (!url) return Alert.alert("Error", "Enter a URL");

    setLoading(true);
    try {
      const res = await fetch("http://192.168.0.7:8000/v1/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      Alert.alert("Error", "API not reachable. Is backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>TrustLens AI</Text>
      <TextInput
        style={styles.input}
        placeholder="Paste URL (e.g. bbc.com)"
        value={url}
        onChangeText={setUrl}
        autoCapitalize="none"
      />
      <Button
        title={loading ? "Checking..." : "Check Truth"}
        onPress={checkUrl}
        disabled={loading}
      />

      {result && (
        <View style={styles.result}>
          <Text style={styles.score}>Score: {result.score}/100</Text>
          {result.evidence.map((e: any, i: number) => (
            <Text key={i} style={styles.evidence}>
              • {e.title}: {e.summary}
            </Text>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: "center" },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  result: {
    marginTop: 20,
    padding: 15,
    backgroundColor: "#f0f0f0",
    borderRadius: 8,
  },
  score: { fontSize: 24, fontWeight: "bold", color: "#1a73e8" },
  evidence: { marginTop: 5, fontSize: 16 },
});
