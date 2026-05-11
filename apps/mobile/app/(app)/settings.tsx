import { View, Text, StyleSheet } from 'react-native'

export default function SettingsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Paramètres</Text>
      <Text style={styles.subtitle}>Compte et préférences</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0A0A', justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 28, fontFamily: 'serif', color: '#F5F0E8' },
  subtitle: { fontSize: 14, color: '#9A9185', marginTop: 8 },
})
