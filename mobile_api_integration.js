// Import necessary libraries
import axios from 'axios';

// Define the API integration component
const MobileAPIIntegration = () => {
  const fetchItems = async () => {
    try {
      const response = await axios.get('https://api.example.com/items');
      console.log(response.data);
    } catch (error) {
      console.error('Error fetching items:', error);
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Fetching items...</Text>
      <Button title='Fetch Items' onPress={fetchItems} />
    </View>
  );
};

export default MobileAPIIntegration;