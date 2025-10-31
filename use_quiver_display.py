import quiver_display as qd

vectorx = [1,0,0]
vectory = [0,1,0]

frame = qd.QuiverDisplay()
frame.add_vector("Vector X", vectorx, color='#FF0000')
frame.add_vector("Test", vectory, color='#0000FF')
step = 0
while True:
    step = step+1
    if step > 2:
        step = 0
    match step:
        case 0:
            vectorx = [2,0,0]
            vectory = [0,1,1]
        case 1 :
            vectorx = [0,1,0]
            vectory = [1,1,0]
        case 2 :
            vectorx = [0,0,1]
            vectory = [1,0,1]
            
    frame.update_vector("Vector X", vectorx)
    frame.update_vector("Test", vectory)
    frame.show()