import { View, Text, StyleSheet } from 'react-native'
import { Link } from 'expo-router'

export default function MobileHome() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>VFS</Text>
      <Text style={styles.subtitle}>Virtual Fashion Studio</Text>
      <View style={styles.links}>
        <Link href="/(app)/studio" style={styles.link}>
          <Text style={styles.linkText}>Studio</Text>
        </Link>
        <Link href="/(app)/dressing" style={styles.link}>
          <Text style={styles.linkText}>Dressing</Text>
        </Link>
        <Link href="/(app)/stylist" style={styles.link}>
          <Text style={styles.linkText}>AI Stylist</Text>
        </Link>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0A0A', justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 48, fontFamily: 'serif', color: '#F5F0E8', fontWeight: '300' },
  subtitle: { fontSize: 16, color: '#9A9185', marginTop: 8 },
  links: { flexDirection: 'row', gap: 16, marginTop: 48 },
  link: { paddingVertical: 12, paddingHorizontal: 24, borderRadius: 8, backgroundColor: '#111111', borderWidth: 1, borderColor: '#2E2E2E' },
  linkText: { color: '#F5F0E8', fontSize: 14 },
})
