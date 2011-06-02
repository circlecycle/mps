import os, smtplib, mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64

from mps.bin.Settings import email_user, email_password

class GMail:
    def __init__(self, recipient, subject, text, *attachmentFilePaths):
        self.sendMail(recipient, subject, text, *attachmentFilePaths)
        
    def sendMail(self, recipient, subject, text, *attachmentFilePaths):        
        msg = MIMEMultipart()
        msg['From'] = email_password
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        
        for attachmentFilePath in attachmentFilePaths:
            msg.attach(getAttachment(attachmentFilePath))
          
        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(email_user, email_password)
        mailServer.sendmail(email_user, recipient, msg.as_string())
        mailServer.close()
        print('Sent email to %s' % recipient)
      
    def getAttachment(self, attachmentFilePath):
        contentType, encoding = mimetypes.guess_type(attachmentFilePath)
        
        if contentType is None or encoding is not None:
            contentType = 'application/octet-stream'
          
        mainType, subType = contentType.split('/', 1)
        
        file = open(attachmentFilePath, 'rb')
        
        if mainType == 'text':
            attachment = MIMEText(file.read())
        elif mainType == 'message':
            attachment = email.message_from_file(file)
        elif mainType == 'image':
            attachment = MIMEImage(file.read(),_subType=subType)
        elif mainType == 'audio':
            attachment = MIMEAudio(file.read(),_subType=subType)
        else:
            attachment = MIMEBase(mainType, subType)
          
        attachment.set_payload(file.read())
        encode_base64(attachment)
        
        file.close()
        
        attachment.add_header('Content-Disposition', 'attachment',   filename=os.path.basename(attachmentFilePath))
        
        return attachment
 
#set a module level attribute to the email service to use.
EmailService = GMail
      
if __name__ == "__main__":
    EmailService("circlecycle@gmail.com", "Test", "This is the text")
    