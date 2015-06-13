class Ani(object):
    """
    Creates an animation given the cell width, height, and the image and it returns the image needed at the time passed
    in seconds
    """

    def __init__(self,num,speed):
        self.speed_max = speed
        self.speed = speed
        self.finished = False
        self.run = 0
        self.rev = False
        self.ani_num = 0
        self.ani_num_max = num

    def reset(self):
        self.speed = self.speed_max
        self.ani_num = 0
        self.finished = False

    def get_frame(self,tick):
        self.speed -= tick
        if self.speed <= 0:
            self.speed = self.speed_max
            self.ani_num += 1
            if self.ani_num == self.ani_num_max:
                self.finished = True
                self.ani_num = 0
                return self.ani_num
            else:
                return self.ani_num
        return self.ani_num

    def get_full_frame(self,tick):
        self.run -= 1
        self.speed -= tick
        if self.speed <= 0:
            self.speed = self.speed_max
            if self.rev == False:
                self.ani_num += 1
            else:
                self.ani_num -=1
            if self.ani_num == self.ani_num_max:
                self.ani_num = self.ani_num_max-1
                self.run = 1
                self.rev = True
                return self.ani_num
            if self.ani_num == 0:
                self.finished = True
                self.rev = False
            else:
                return self.ani_num
        return self.ani_num


