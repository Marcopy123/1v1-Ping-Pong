import cv2

class mpHands:
    import mediapipe as mp
    def __init__(self, maxHands = 2, tol1 = 0.5, tol2 = 0.5):
        self.hands = self.mp.solutions.hands.Hands(False, maxHands, tol1, tol2)
    
    def Marks(self, frame):
        myHands = []
        handsType = []
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRGB)

        if results.multi_hand_landmarks != None:
            for hand in results.multi_handedness:
                handType = hand.classification[0].label
                handsType.append(handType)
            for handLandMarks in results.multi_hand_landmarks:
                myHand = []
                for landmark in handLandMarks.landmark:
                    myHand.append((int(landmark.x*width), int(landmark.y*height)))
                
                myHands.append(myHand)
        
        return myHands, handsType

width = 1280
height = 690

cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)

cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cam.set(cv2.CAP_PROP_FPS, 30)
cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))

findHands = mpHands(2, 0.5, 0.5)


paddleHeight = int(width / 10)
paddleWidth = int(paddleHeight / 5)

paddleColorUser1 = (0, 0, 255)
paddleColorUser2 = (255, 0, 0)

deltaX = 12
deltaY = 10

xPos = int(width / 2)
yPos = int(height / 2)
radius = 20

redScore = 0
blueScore = 0

while True:
    ignore,  frame = cam.read()
    frame = cv2.resize(frame, (width, height))

    handData, handsType = findHands.Marks(frame)

    leftHandYPos = 0
    rightHandYPos = 0

    for hand, handType in zip(handData, handsType):
        if handType == "Right": # this is the left hand
            cv2.rectangle(frame, (10, int(hand[8][1] + paddleHeight/2)), (paddleWidth+10, int(hand[8][1] - paddleHeight/2)), paddleColorUser1, -1)
            rightHandYPos = hand[8][1]

        if handType == "Left": # this is the right hand
            cv2.rectangle(frame, (width - paddleWidth - 10, int(hand[8][1] + paddleHeight/2)), (width-10, int(hand[8][1] - paddleHeight/2)), paddleColorUser2, -1)
            leftHandYPos = hand[8][1]

    if yPos - radius >= 0:
        deltaY = -deltaY
    
    if yPos + radius <= height:
        deltaY = -deltaY
    
    if xPos + radius >= width - paddleWidth - 10:
        if int(leftHandYPos + paddleHeight/2) >= yPos and int(leftHandYPos - paddleHeight/2) <= yPos:
            deltaX = -deltaX 

    if xPos - radius <= 0:
        redScore += 1
        xPos = int(width / 2)
        yPos = int(height / 2)

        
    if xPos - radius <= 10 + paddleWidth:
        if int(rightHandYPos + paddleHeight/2) >= yPos and int(rightHandYPos - paddleHeight/2) <= yPos:
            deltaX = -deltaX

    if xPos + radius >= width:
        blueScore += 1
        xPos = int(width / 2)
        yPos = int(height / 2)
        
    
    xPos += deltaX
    yPos += deltaY

    cv2.circle(frame, (xPos, yPos), radius, (0, 255, 0), -1)

    cv2.putText(frame, str(blueScore) + "-" + str(redScore), (int(width/2 - 50), 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 1)

    cv2.imshow('1v1 Pong', frame)
    cv2.moveWindow('1v1 Pong', 0, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
