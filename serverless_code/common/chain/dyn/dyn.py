def dyn(events):
    for event in events:
        if event.get('eventName') == 'INSERT':
            new_image = event.get('dynamodb').get('NewImage')
            print(f"New image received: {new_image}")

            id = new_image.get('id').get('S')
            sender, receiver, amount = new_image.get('sender').get('S'), new_image.get('receiver').get('S'), new_image.get('amount').get('N')
            print(f"sender: {sender}, receiver: {receiver}, amount: {amount}")
