#very simple encoding scheme

class CommaDelimitedEncoder:
    """
    comma delimited data to serial encoding from python to arduino
    
    """
    
    def __init__(self, 
                 begin_message = '<',
                 end_message = '>',
                 begin_system_message = '[',
                 serial_format = 'utf-8',
                ):
        
        self.begin_message = begin_message
        self.end_message = end_message
        self.serial_format = serial_format
        
    def encode_data(self, data):
        """
        takes angle a list of data and converts to message to send to 
        the arduino. example
        
        >>> CDE = CommaDelimitedEncoder()
        >>> data = [1,3,4]
        >>> CDE.encode_data(data)
        b'<1,3,4>
    
        """
        encoded_message = self.begin_message
        l = len(data)
        for i, msg in enumerate(data):
            encoded_message += str(msg)
            if i < l-1: 
                encoded_message += ','
  
        encoded_message += self.end_message
        return encoded_message.encode(self.serial_format)
    
    def encode_system_message(self, data):
        """
        placeholder for future iterations
        """
        pass
    