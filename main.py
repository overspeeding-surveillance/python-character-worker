import torch
import cv2
import uuid
from custom_utils.capture import capture_character
from custom_utils.sort import sort
import pika
import sys
import os

THIRD_PYTHON_QUEUE = "THIRD_PYTHON_QUEUE"
FOURTH_PYTHON_QUEUE = "FOURTH_PYTHON_QUEUE"

model = torch.hub.load("ultralytics/yolov5", "custom",
                       path="best.pt", force_reload=True)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=THIRD_PYTHON_QUEUE)

    def callback_function(ch, method, properties, body):
        print(" [x] Received %r" % body)
        number_plate_img_path = "../number_plates/" + str(body.decode())

        if not os.path.exists(number_plate_img_path):
            return

        results = model(number_plate_img_path)
        [readable_result] = results.pandas().xyxy

        img = cv2.imread(number_plate_img_path, 0)

        foldername = str(uuid.uuid4())

        list = []
        top_characters_list = []
        bottom_characters_list = []

        # total ymax height
        total_height = 0

        # if the detection is above the mean than its a top character and vice versa
        for i in range(0, len(readable_result)):
            xmin = int(readable_result['xmin'][i])
            ymin = int(readable_result['ymin'][i])
            xmax = int(readable_result['xmax'][i])
            ymax = int(readable_result['ymax'][i])
            total_height = total_height + ymax
            list.append([xmin, ymin, xmax, ymax])

        if len(list) == 0:
            return

        mean_height = total_height / len(list)

        for detection in list:
            if detection[3] < mean_height:
                top_characters_list.append(detection)
            else:
                bottom_characters_list.append(detection)

        top_characters_list = sort(top_characters_list)
        bottom_characters_list = sort(bottom_characters_list)

        sorted_list = top_characters_list + bottom_characters_list

        for i in range(0, len(sorted_list)):
            filename = str(i) + ".jpg"
            capture_character(img, sorted_list[i][0], sorted_list[i][1],
                              sorted_list[i][2], sorted_list[i][3], foldername, filename)
            channel.basic_publish(
                exchange='', routing_key=FOURTH_PYTHON_QUEUE, body=foldername)
            print(" [x] Sent " + foldername)

    channel.basic_consume(
        queue=THIRD_PYTHON_QUEUE, on_message_callback=callback_function, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
