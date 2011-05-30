# import modules
import smtplib
from email.MIMEText import MIMEText

#Astun
import OutPut, ConfigParse

class sendEmail():

	def __init__(self, Out):
		
		opts = ConfigParse.OptParser()
		
		#Output
		self.out = Out
		
	def sendEmail(self, email_subject, email_body):
		""" Function for sending email given a sender, recipient, reply-to, subject, and body"""
		
		try:
			self.emailcreds = opts.ConfigSectionMap('Email')
			self.email_sender = self.emailcreds['email_sender']
			self.email_recip = self.emailcreds['email_recip']
			self.smtp_address = self.emailcreds['smtp_address']
	
			msg = MIMEText(email_body)
			msg['Subject'] = email_subject
			msg['From'] = self.email_sender
			msg['Reply-to'] = self.email_sender
			msg['To'] = self.email_recip
	
			# Establish an SMTP object and connect to mail server
			s = smtplib.SMTP(self.smtp_address)  

			# Send the email
			try:
				s.sendmail(self.email_sender,self.email_recip, msg.as_string())
				s.quit()
				print "Successfully sent email", email_subject
			except:
   				print "Error: unable to send email", email_subject
		except:
			self.out.OutputInfo("No email settings defined")
		






