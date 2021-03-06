# ex -> https://qiita.com/comachi/items/c494e0d6c6d1775a3748
# ex2 -> https://github.com/Adam-Langley/pybleno
# uuid -> https://www.uuidgenerator.net/version4

from pybleno import *
import binascii

bleno = Bleno()

MY_SERVICE_UUID = '13333333-3333-3333-3333-333333333310'
NOTIFY_CHARACTERISTIC_UUID = '13333333-3333-3333-3333-333333333311'
READ_CHARACTERISTIC_UUID = '13333333-3333-3333-3333-333333333312'
WRITE_CHARACTERISTIC_UUID = '13333333-3333-3333-3333-333333333313'
DEVICE_NAME = 'WDJ'

counter = 0

########## ########## ########## ########## ##########

# Characteristic -> bleno inheritance / node ->util.inherits(XX, Characteristic);
class NotifyCharacteristic(Characteristic):
  def __init__(self):
    Characteristic.__init__(self, {
      'uuid': NOTIFY_CHARACTERISTIC_UUID,
      'properties': ['notify'],
      'value': None
    })
    self._value = 0
    self._updateValueCallback = None

  def onSubscribe(self, maxValueSize, updateValueCallback):
    print('Characteristic - onSubscribe')
    self._updateValueCallback = updateValueCallback
  def onUnsubscribe(self):
    print('Characteristic - onUnsubscribe')
    self._updateValueCallback = None

class ReadCharacteristic(Characteristic):
  def __init__(self):
    Characteristic.__init__(self, {
      'uuid': READ_CHARACTERISTIC_UUID,
      'properties': ['read','notify'],
      'value': None
    })
    self._value = 0
    self._updateValueCallback = None

  def onSubscribe(self, maxValueSize, updateValueCallback):
    print('ReadCharacteristic - onSubscribe')
    self._updateValueCallback = updateValueCallback
  def onUnsubscribe(self):
    print('ReadCharacteristic - onUnsubscribe')
    self._updateValueCallback = None
  # def onReadRequest(self, offset, callback):
  #   # B == unsigned char int 1btyes
  #   data = array.array('B', [0] * 2) # [0,]
  #   # writeUInt8(buffer, value, offset)
  #   print(data)
  #   # callback(Characteristic.RESULT_SUCCESS, self._value)
  #   callback(Characteristic.RESULT_SUCCESS, data)

  def onReadRequest(self, offset, callback):
    data = array.array('b', [5]*20) # or data = bueffer
    writeUInt8(data, 100, 1)
    writeUInt8(data, 120, 2)
    writeUInt8(data, 100, 3)
    writeUInt8(data, 120, 4)
    print("onReadRequest")
    print(data)
    callback(Characteristic.RESULT_SUCCESS, data)


class WriteCharacteristic(Characteristic):
  def __init__(self):
    Characteristic.__init__(self, {
      'uuid': WRITE_CHARACTERISTIC_UUID,
      'properties': ['write','notify'],
      'value': None
    })
    self._value = 0
    self._updateValueCallback = None

  def onSubscribe(self, maxValueSize, updateValueCallback):
    print('Characteristic - onSubscribe')
    self._updateValueCallback = updateValueCallback
  def onUnsubscribe(self):
    print('Characteristic - onUnsubscribe')
    self._updateValueCallback = None

  def onWriteRequest(self, data, offset, withoutResponse, callback):
    print('onWriteRequest', end='')
    print(data)
    callback(Characteristic.RESULT_SUCCESS)


########## ########## ########## ########## ##########

def onStateChange(state):
  print('on -> stateChange: ' + state)
  if (state == 'poweredOn'):
    bleno.startAdvertising(DEVICE_NAME, [MY_SERVICE_UUID])
  else:
    bleno.stopAdvertising()

bleno.on('stateChange', onStateChange)

notifyCharacteristic = NotifyCharacteristic()
readCharacteristic = ReadCharacteristic()
writeCharacteristic = WriteCharacteristic()

def onAdvertisingStart(error):
  print('on -> advertisingStart: ' + ('error ' + error if error else 'success'))
  if not error:
    bleno.setServices([
      BlenoPrimaryService({
        'uuid': MY_SERVICE_UUID,
        'characteristics': [
          notifyCharacteristic,
          readCharacteristic,
          writeCharacteristic
        ]
      })
    ])

bleno.on('advertisingStart', onAdvertisingStart)
bleno.start()

########## ########## ########## ########## ##########

import time
def task():
  global counter
  counter += 1
  if counter > 10:
    counter = 1
  notifyCharacteristic._value = counter
  if notifyCharacteristic._updateValueCallback:
    #  value  ->  str().encode()  ->  '12'  ->  [49, 50]
    # 'b' <class 'bytes'>
    # print('Sending notification with value : ' + str(notifyCharacteristic._value))
    # notificationBytes = str(notifyCharacteristic._value).encode()
    # print(notificationBytes)

    # data = array.array('b', [5]*10)
    # writeUInt8(data, 30, 1)
    # writeUInt8(data, 40, 2)
    # print(data)

    data = array.array('b', [0]*5)
    writeUInt8(data, counter, 0)
    notifyCharacteristic._updateValueCallback(data)

  if readCharacteristic._updateValueCallback:
    data = array.array('b', [0]*10)
    writeUInt8(data, 1, 1)
    writeUInt8(data, 2, 2)
    writeUInt8(data, 3, 3)
    writeUInt8(data, 1, 4)
    writeUInt8(data, 2, 5)
    writeUInt8(data, 3, 6)
    readCharacteristic._updateValueCallback(data)

  if writeCharacteristic._updateValueCallback:
    data = array.array('b', [0]*15)
    writeUInt8(data, 4, 1)
    writeUInt8(data, 5, 2)
    writeUInt8(data, 6, 3)
    writeUInt8(data, 4, 4)
    writeUInt8(data, 5, 5)
    writeUInt8(data, 6, 6)
    writeCharacteristic._updateValueCallback(data)

while True:
  task()
  time.sleep(1)