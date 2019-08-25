import re 

def verifyEmailId(emailId):  
  
    # pass the regualar expression 
    # and the string in search() method 
    if (re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$',emailId))==None:   
        print('msg : emailId is not valid.')

verifyEmailId("ankitrai326@gmail.com")