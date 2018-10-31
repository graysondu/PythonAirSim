# 这个文件主要关于使用AirSim的Python接口的心得

## Python APIs

- 使用诸如client.moveByVelocityAsync(1,0,0,100)这种API的时候，如果在后面加入了.join()，则程序会等待API进程执行完毕，然后再执行Python程序的下一步，但是实际中我们往往需要在飞机移动的过程中，处理图像，然后改变飞机的指令，这个时候就不能使用client.moveByVelocityAsync(1,0,0,100).join()，而是简单的使用client.moveByVelocityAsync(1,0,0,100)即可。这样，指令发送完毕后Python会继续往下进行。PS：这个结论是学习多线程编程的时候想到的，送给需要的朋友。

## Python Library

- time.sleep(seconds), seconds可以为小数

- 不同线程间数据判断或使用，用线程锁threading.Lock()，举例说明: python--多线程编程中的线程间通信的问题--变量同步锁，我定义两个线程类，第一个用来不停的累加一个全局变量，第二个用来检测那个全局变量是否累加到5，如果累加到了5，就输出，并停止线程。

  ```
  import threading
  import time
   
  counter = 0
  mutex = threading.Lock()
   
  class MyThread(threading.Thread):
      def __init__(self):
          threading.Thread.__init__(self)
   
      def run(self):
          global counter, mutex
          while True:
              time.sleep(1);
              if mutex.acquire():
                  counter += 1
                  if counter == 10:
                      break
                  print "I am %s, set counter:%s" % (self.name, counter)
                  mutex.release()
   
  class ZyThread(threading.Thread):
      def __init__(self):
          threading.Thread.__init__(self)
   
      def run(self):
          global counter,mutex
          while True:
              time.sleep(1)
              if mutex.acquire():
                  if counter == 5:
                      print "I am %s, Now is Number5" % (self.name)
                      mutex.release()
                      break
                  print "I am %s------------" % (self.name)
                  mutex.release()
   
  if __name__ == "__main__":
      my_thread = MyThread()
      my_thread.start()
      zy_thread = ZyThread()
      zy_thread.start()
  ```

- 
