/* app/(tabs)/index.tsx */

import { View, Text, StyleSheet } from "react-native";
import { Link } from "expo-router";

export default function Home() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>TrustLens AI</Text>
      <Text style={styles.subtitle}>Global Truth Engine</Text>
      <Link href="/score" style={styles.button}>
        <Text style={styles.buttonText}>Start Checking →</Text>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  title: { fontSize: 32, fontWeight: "bold" },
  subtitle: { fontSize: 18, color: "#666", marginVertical: 10 },
  button: {
    marginTop: 30,
    padding: 15,
    backgroundColor: "#1a73e8",
    borderRadius: 8,
  },
  buttonText: { color: "white", fontWeight: "bold" },
});
