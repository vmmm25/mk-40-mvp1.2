---
name: react-native-mobile
version: 1.0.0
description: Desarrollo de aplicaciones móviles con React Native y Expo. Usa cuando construyas apps iOS/Android, manejes navegación nativa, accedas a APIs del dispositivo, o despliegues en tiendas de apps.
tags: [react-native, expo, mobile, ios, android, navigation, app-store]
author: garri333
license: MIT
source: https://skills.sh/vercel-labs/agent-skills/vercel-react-native-skills
---

# React Native Mobile Skill

## Cuándo usar esta skill
- Crear una app móvil iOS/Android con React Native
- Trabajar con Expo (managed o bare workflow)
- Implementar navegación, gestos, animaciones nativas
- Acceder a cámara, GPS, notificaciones push, biometría
- Preparar una app para App Store / Google Play

## Arquitectura recomendada

```
src/
├── app/              # Expo Router (basado en archivos, como Next.js)
│   ├── (tabs)/       # Tab navigation
│   │   ├── index.tsx
│   │   └── profile.tsx
│   ├── _layout.tsx   # Root layout
│   └── modal.tsx
├── components/       # Componentes reutilizables
│   ├── ui/           # Componentes de UI primitivos
│   └── features/     # Componentes de feature
├── hooks/            # Custom hooks
├── services/         # API calls, auth, storage
├── store/            # Estado global (Zustand/Jotai)
├── utils/            # Utilidades
└── constants/        # Colores, sizes, etc.
```

## Setup inicial con Expo

```bash
# Crear proyecto con Expo Router (recomendado)
npx create-expo-app@latest mi-app --template

# Instalar dependencias esenciales
npx expo install expo-router expo-constants
npx expo install @react-navigation/native @react-navigation/bottom-tabs
npx expo install react-native-safe-area-context react-native-screens

# Iniciar en desarrollo
npx expo start

# Ejecutar en iOS/Android (con simulador)
npx expo run:ios
npx expo run:android
```

## Navegación con Expo Router

```tsx
// app/_layout.tsx — Root Layout
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
    </Stack>
  );
}

// app/(tabs)/_layout.tsx — Tab Navigation
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#2B5CE6' }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Inicio',
          tabBarIcon: ({ color }) => <Ionicons name="home" size={24} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Perfil',
          tabBarIcon: ({ color }) => <Ionicons name="person" size={24} color={color} />,
        }}
      />
    </Tabs>
  );
}

// Navegar programáticamente
import { router } from 'expo-router';
router.push('/detail/123');
router.replace('/login');
router.back();
```

## Componentes y estilos

```tsx
import { View, Text, StyleSheet, Pressable, ScrollView, FlatList } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// ✅ Componente responsivo con safe area
function HomeScreen() {
  const insets = useSafeAreaInsets();
  
  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={[
        styles.content,
        { paddingBottom: insets.bottom + 20 }
      ]}
    >
      <Text style={styles.title}>Bienvenido</Text>
      
      {/* FlatList para listas largas (mejor performance que map) */}
      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ItemCard item={item} />}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        showsVerticalScrollIndicator={false}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  content: { padding: 16 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 16 },
  separator: { height: 1, backgroundColor: '#E5E7EB', marginVertical: 8 },
});

// ✅ Platform-specific styles
import { Platform } from 'react-native';
const shadowStyle = Platform.select({
  ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4 },
  android: { elevation: 4 },
});
```

## APIs nativas más usadas

### Cámara y galería
```tsx
import * as ImagePicker from 'expo-image-picker';

async function pickImage() {
  const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (!permission.granted) return;
  
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    allowsEditing: true,
    aspect: [4, 3],
    quality: 0.8,
  });
  
  if (!result.canceled) {
    const imageUri = result.assets[0].uri;
    // Usar imageUri
  }
}

async function takePhoto() {
  const permission = await ImagePicker.requestCameraPermissionsAsync();
  if (!permission.granted) return;
  
  const result = await ImagePicker.launchCameraAsync({
    quality: 0.8,
  });
  
  if (!result.canceled) {
    return result.assets[0].uri;
  }
}
```

### Notificaciones push
```tsx
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

async function registerForPushNotifications() {
  if (!Device.isDevice) return null;
  
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  
  if (finalStatus !== 'granted') return null;
  
  const token = await Notifications.getExpoPushTokenAsync({
    projectId: process.env.EXPO_PUBLIC_PROJECT_ID,
  });
  
  return token.data;
}

// Escuchar notificaciones
Notifications.addNotificationReceivedListener((notification) => {
  console.log('Notificación recibida:', notification);
});
```

### AsyncStorage (persistencia local)
```tsx
import AsyncStorage from '@react-native-async-storage/async-storage';

// Guardar
await AsyncStorage.setItem('user_token', token);
await AsyncStorage.setItem('user_data', JSON.stringify(userData));

// Leer
const token = await AsyncStorage.getItem('user_token');
const userData = JSON.parse(await AsyncStorage.getItem('user_data') || 'null');

// Borrar
await AsyncStorage.removeItem('user_token');
```

## Preparar para producción

### app.json / app.config.js
```json
{
  "expo": {
    "name": "Mi App",
    "slug": "mi-app",
    "version": "1.0.0",
    "platforms": ["ios", "android"],
    "ios": {
      "bundleIdentifier": "com.empresa.miapp",
      "buildNumber": "1",
      "infoPlist": {
        "NSCameraUsageDescription": "Necesitamos acceso a la cámara para..."
      }
    },
    "android": {
      "package": "com.empresa.miapp",
      "versionCode": 1,
      "permissions": ["CAMERA", "READ_EXTERNAL_STORAGE"]
    }
  }
}
```

### Build con EAS (Expo Application Services)
```bash
# Instalar EAS CLI
npm install -g eas-cli
eas login

# Configurar
eas build:configure

# Build para tiendas
eas build --platform android --profile production
eas build --platform ios --profile production

# Submit directo a tiendas
eas submit --platform android
eas submit --platform ios

# OTA Updates (sin pasar por revisión de tienda)
eas update --branch production --message "Fix: corrección de bug en perfil"
```

## Referencias
- [Expo documentation](https://docs.expo.dev/)
- [Expo Router](https://expo.github.io/router/)
- [React Native documentation](https://reactnative.dev/docs/getting-started)
- [EAS Build](https://docs.expo.dev/build/introduction/)
