/* app/_layout.tsx */
import { Tabs } from "expo-router";
import { Text } from "react-native";

export default function Layout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "#1a73e8",
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: () => <Text>🏠</Text>,
        }}
      />
      <Tabs.Screen
        name="score"
        options={{
          title: "Check",
          tabBarIcon: () => <Text>🔍</Text>,
        }}
      />
    </Tabs>
  );
}
