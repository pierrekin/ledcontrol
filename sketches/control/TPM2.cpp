/*
TPM2 protocol for LED comunications (TPM2.serial)
Copyright (C) 2019  Stephan Ruloff

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; in version 2 only
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
*/

#include "TPM2.h"

TPM2::TPM2(uint8_t *data, uint16_t len)
{
  mBuffer = data;
  mBufferLen = len;
  mPosRx = 0;
  mState = WAIT_SYNC;
  mType = TYPE_DATA;
  mCbRxData = 0;
}
void TPM2::registerRxData(TpmCallback cb)
{
  mCbRxData = cb;
}

void TPM2::update(uint8_t lastByte)
{
  switch (mState)
  {
  case WAIT_SYNC:
    if (TPM2_START == lastByte)
    {
      mState = HEADER1;
    }
    break;
  case HEADER1:
    if (TPM2_TYPE_DATA == lastByte)
    {
      mType = TYPE_DATA;
      mState = HEADER2;
    }
    else if (TPM2_TYPE_CMD == lastByte)
    {
      mType = TYPE_COMMAND;
      mState = HEADER2;
    }
    else if (TPM2_TYPE_RESP == lastByte)
    {
      mType = TYPE_RESPONSE;
      mState = HEADER2;
    }
    else
    {
      // unknown is fail!
      mState = WAIT_SYNC;
    }
    break;
  case HEADER2:
    mLen = lastByte << 8;
    mState = HEADER3;
    break;
  case HEADER3:
    mLen |= lastByte;
    mState = DATA;
    mPosCounter = 0;
    break;
  case DATA:
    if (mBufferLen > mPosCounter)
    {
      mBuffer[mPosCounter] = lastByte;
    }
    mPosCounter++;
    if (mPosCounter == mLen)
    {
      mState = END;
    }
    break;
  case END:
    if (TPM2_END == lastByte)
    {
      // ok
      if (mCbRxData && mType == TYPE_DATA)
      {
        mCbRxData(mBuffer, min(mLen, mBufferLen));
      }
    }
    mState = WAIT_SYNC;
    break;
  }
}
