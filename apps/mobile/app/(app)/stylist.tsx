import { View, Text, StyleSheet } from 'react-native'

export default function StylistScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>AI Stylist</Text>
      <Text style={styles.subtitle}>Conseils personnalisés</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0A0A', justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 28, fontFamily: 'serif', color: '#F5F0E8' },
  subtitle: { fontSize: 14, color: '#9A9185', marginTop: 8 },
})
