import face_recognition
import cv2
import numpy
import time
import pid
import servo_control

# video_capture = cv2.VideoCapture(0)
# video_height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
# video_width  = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
# video_center = (int(video_width//2), int(video_height//2))


# face_locations = []
# process_this_frame = True

# xPID = pid.PIDController(.001)
# yPID = pid.PIDController(.001)
# xPID.initialize()
# yPID.initialize()

# Servo = servo_control.PanTiltServo(start_point=(90, 70), flip_x=False, flip_y=False)
# Servo.reset()
# time.sleep(2)

while True:

    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = small_frame[:, :, ::-1]

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)


    process_this_frame = not process_this_frame
    font = cv2.FONT_HERSHEY_DUPLEX

    for (top, right, bottom, left) in face_locations:
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2
        
        target = ((right+left)//2, (top+bottom)//2)
        target_print = f'{target[0]},{target[1]}'
        
        error = (target[0] - video_center[0], target[1] - video_center[1])
        error_text = f'x error = {error[0]}, y error = {error[1]}'

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, target_print , (left, bottom + 10), font, .5, (0, 0, 255), 1)
        cv2.circle(frame,video_center, 10, (0,0,255), -1)
        cv2.circle(frame, target, 4, (0,255,0), -1)
        
        cv2.putText(frame, error_text , (10, 30), font, .75, (0, 0, 255), 1)
        
        move_x = xPID.update(error[0], sleep=.01)
        move_y = xPID.update(error[1], sleep=.01)
        
        Servo.move(move_x, move_y)


    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
Servo.close()