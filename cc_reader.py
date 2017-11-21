import sys, os, re
import argparse
import serial
import time

SBEGIN_NVER =          b'\x01,\x00'
SBEGIN      =          b'\x01'
SDATA       =          b'\x02'
SRSP        =          b'\x03'
SEND        =          b'\x04'
ERRO        =          b'\x05'
READ_FLASH  =          b'\x06'
READ_CHIPID =          b'\x07'
SAY_HELLO   =          b'\x08'


def main(N):
	
  print("connecting to COM", args.sport, "and reading", args.num, "kb to", args.file)

  port = "COM1"
  if int(args.sport) < 10:
    port = "COM%s" % args.sport
  else:
    port = "\\\\.\\COM%s" % args.sport

  s = serial.Serial(port, 115200, timeout=3, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)


  # start debugger
  s.write(SBEGIN_NVER) # SBEGIN, no verification
  time.sleep(0.1)
  
  if (s.read() == b'w'):
      print("programmer connected")
  
  i = 0
  xxx = 0
  while xxx != b'\xEA':
      xxx = s.read()
      time.sleep(0.1)
      #print(".", xxx)
      i = i + 1
      if i > 30:
          return
  
  s.write(READ_CHIPID)
  time.sleep(0.1)

  chip = s.read(1)

  if len(chip) == 0:
      print("no chip detected\nabort")
      return

  print("Detected CHIP (ID): ", int.from_bytes(chip, byteorder='little'))
  sys.stdout.flush()

  endaddr = int(int(args.num) * 1024 / (4 * 128))

  with open(args.file, 'ab') as f:
    for addr in range(0, endaddr, 1):
      #print("read from %04x" % addr)
      #print(bytes([addr]))
      sys.stdout.flush()
      s.write(READ_FLASH + bytes([addr]))


      time.sleep(0.1)
      r = s.read(512)
      #print(len(r))
      #print(r)

      if len(r) < 512:
          print("failed to read flash content\nABORT!", r)
          return
    
      sys.stdout.write("y")
      sys.stdout.flush()
      time.sleep(0.1)
      f.write(r)

  print("\nread flash succesfully")
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="reads ti cc chips")
    parser.add_argument('--file', '-f', help='file to write flash data to')
    parser.add_argument('--sport', '-p', help='port')
    parser.add_argument('--num', '-n', default = 128, help='bytes to read (kb)')
    args = parser.parse_args()

    sys.exit(main(str(args.file)))

