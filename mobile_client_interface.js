// Import necessary libraries
import React from 'react';
import { View, Text, Button } from 'react-native';

// Define the mobile client interface component
const MobileClientInterface = () => {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Welcome to the Mobile Client Interface</Text>
      <Button title='Fetch Items' onPress={() => console.log('Fetching items...')} />
    </View>
  );
};

export default MobileClientInterface;