from kafka import KafkaProducer
import time

producer = KafkaProducer(bootstrap_servers=['localhost:29192', 'localhost:29292', 'localhost:29392'])

i = 0
while True:
    try:
        producer.send('critical_data', value=f"msg {i}".encode('utf-8')).get(timeout=2)
        print(f"Sent: {i}")
        i += 1
    except Exception as e:
        print(f"Error sending {i}: {e}")
    
    time.sleep(0.5)