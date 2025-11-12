/* app/(tabs)/score.tsx */

import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  Alert,
  ScrollView,
} from "react-native";

export default function ScoreScreen() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // CHANGE THIS TO YOUR PC's IP (run `ipconfig`)
  const API_URL = "http://192.168.0.7:8000/v1/score";

  const checkUrl = async () => {
    if (!url) return Alert.alert("Error", "Enter a URL");
    if (!url.startsWith("http")) setUrl("https://" + url);

    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error("API error");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      Alert.alert(
        "Error",
        `Check your PC IP or API. Is backend running?\n\n${err}`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Check Truth</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g. bbc.com"
        value={url}
        onChangeText={setUrl}
        autoCapitalize="none"
      />
      <Button
        title={loading ? "Analyzing..." : "Check"}
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
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#fff" },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    textAlign: "center",
    marginVertical: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },
  result: {
    marginTop: 25,
    padding: 18,
    backgroundColor: "#f8f9fa",
    borderRadius: 12,
    borderLeftWidth: 5,
    borderLeftColor: "#1a73e8",
  },
  score: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#1a73e8",
    marginBottom: 10,
  },
  evidence: { fontSize: 16, marginVertical: 4, color: "#333" },
});
