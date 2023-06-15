#include <Wire.h>
#include <LIS3MDL.h>
#include <LSM6.h>
#include <MadgwickAHRS.h>
#include <PacketSerial.h>

LIS3MDL mag;
LSM6 imu;
Madgwick filter;
PacketSerial packetSerial;

// That being said, the maximum realizable throughput is capped at the maximum allowable baud rate of the device. For instance,
// the CP2102 maximum baud rate is listed as 921600 bps (see CP2102 datasheet, page 1). Assuming the largest frame size you can
// select for the device of 11 bits (8 data bits, 1 start bit, 2 stop bits), the theoretical maximum throughput of the device with
// these settings is 921600 bps / 11 bits per byte = 83781 bytes/sec = 83.781 kB/sec. This is not a guaranteed throughput because
// of the uncertainty of the USB delivery, but serves as a theoretical ceiling on the CP2102 throughput. Thus, the maximum throughput
// is also less than the total number of bits sent due to overhead of the UART protocol (see figure below).

unsigned long sampleControlPrevious = 0;
unsigned long sampleTimingCounter = 0;
unsigned long sampleTimingPrevious = 0;

unsigned long reportControlPrevious = 0;
unsigned long reportTimingCounter = 0;
unsigned long reportTimingPrevious = 0;

const int serialBaud = 921600;

const int sampleTargetFrequency = 1000;                      // Hz
const int microsPerSample = 1000000 / sampleTargetFrequency; // us

const int reportTargetFrequency = 1000; // Hz
const int microsPerReport = 1000000 / reportTargetFrequency;

void setup()
{
  packetSerial.begin(serialBaud);

  Wire.begin();

  if (!imu.init())
  {
    Serial.println("Failed to detect and initialize IMU!");
    while (1)
      ;
  }
  imu.enableDefault();

  imu.writeReg(imu.CTRL2_G, 0x88); // Configure Gyro for 1.66kHz and 1000 dps full scale

  if (!mag.init())
  {
    Serial.println("Failed to detect and initialize magnetometer!");
    while (1)
      ;
  }

  mag.enableDefault();

  filter.begin(sampleTargetFrequency);

  unsigned long microsNow = micros();

  sampleControlPrevious = microsNow;
  sampleTimingPrevious = microsNow;

  reportControlPrevious = microsNow;
  reportTimingPrevious = microsNow;
}

struct imu_sample_s
{
  float gx;
  float gy;
  float gz;
  float ax;
  float ay;
  float az;
  float mx;
  float my;
  float mz;
};

struct attitude_s
{
  float roll;
  float pitch;
  float yaw;
};

struct timing_s
{
  float sf;
  float rf;
};

void loop()
{

  unsigned long microsNow = micros();

  if (microsNow - sampleControlPrevious >= microsPerSample)
  {
    // Time sample
    sampleControlPrevious = microsNow;
    sampleTimingCounter++;

    // Read sample
    mag.read();
    imu.read();

    imu_sample_s imu_sample;

    // Gyro in Degrees per second
    imu_sample.gx = convertRawGyro(imu.g.x);
    imu_sample.gy = convertRawGyro(imu.g.y);
    imu_sample.gz = convertRawGyro(imu.g.z);

    // Accel in g
    imu_sample.ax = convertRawAcceleration(imu.a.x);
    imu_sample.ay = convertRawAcceleration(imu.a.y);
    imu_sample.az = convertRawAcceleration(imu.a.z);

    // Mag in ??
    imu_sample.mx = convertRawMag(mag.m.x);
    imu_sample.my = convertRawMag(mag.m.y);
    imu_sample.mz = convertRawMag(mag.m.z);

    // Process sample
    filter.updateIMU(imu_sample.gx, imu_sample.gy, imu_sample.gz, imu_sample.ax, imu_sample.ay, imu_sample.az);

    // If it's time to report
    if (microsNow - reportControlPrevious > microsPerReport)
    {
      // Time report
      reportControlPrevious = microsNow;
      reportTimingCounter++;

      // Build report

      attitude_s attitude;

      // Attitude in Euler angles
      attitude.roll = filter.getRoll();
      attitude.pitch = filter.getPitch();
      attitude.yaw = filter.getYaw();

      timing_s timing;

      // Frequencies in Hz
      timing.sf = ((float)sampleTimingCounter / (microsNow - sampleTimingPrevious) * 1000000); // Hz
      timing.rf = ((float)reportTimingCounter / (microsNow - reportTimingPrevious) * 1000000); // Hz

      // Note, that there is an additional byte allocated
      uint8_t buffer[1 + sizeof(imu_sample_s) + sizeof(attitude_s) + sizeof(timing_s)] = {0xFF};

      // const uint8_t* attitude_ptr = (uint8_t*) &attitude;
      memcpy(&buffer[1], &attitude, sizeof(attitude));

      // const uint8_t* imu_ptr = (uint8_t*) &imu_sample;
      memcpy(&buffer[1 + sizeof(attitude)], &imu_sample, sizeof(imu_sample));

      // const uint8_t* timing_ptr = (uint8_t*) &timing;
      memcpy(&buffer[1 + sizeof(attitude) + sizeof(imu_sample)], &timing, sizeof(timing));

      // Serial.write((uint8_t) attitude[0], sizeof(float));
      packetSerial.send(buffer, sizeof(buffer));
    }
  }
}

float convertRawGyro(int gRaw)
{
  // Convert to degrees per second
  return (float)gRaw * 0.035;
}

float convertRawAcceleration(int aRaw)
{
  // Convert to g
  return (float)aRaw * 0.000061;
}

float convertRawMag(int mRaw)
{
  // Convert to ??
  return (float)mRaw * 0.000146156;
}