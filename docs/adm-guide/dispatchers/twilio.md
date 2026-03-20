# Twilio SMS Dispatcher

The Twilio SMS dispatcher sends notifications as SMS via Twilio's API.

## Configuration

The following parameters are required to configure the Twilio SMS dispatcher:

- **SID**: Your Twilio Account SID.
- **Token**: Your Twilio Auth Token.
- **Number**: Your Twilio phone number from which the SMS will be sent.

## How to use

1.  Select `SMS (Twilio)` as dispatcher for a Channel
2.  Fill the form with your Twilio Account SID, Auth Token and phone number.
3.  Save the Channel.

Now you can add this channel to your Application and send SMS notifications. The recipient's phone number should be in E.164 format.
