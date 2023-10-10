import smtplib
import time
from datetime import datetime
import pandas as pd

df = pd.read_csv("data2.csv")
print(df)
email_list = list(df['Mail'])
time_list = list(df['time'])
Text_to_sent = list(df['Text'])
t = {}
for i in range(len(Text_to_sent)):
    t[Text_to_sent[i]] = (time_list[i], email_list[i])
print(t)
my_email = "sainathyadlapalli98@gmail.com"
password = "xwhelynbjzhruyie"
is_msg = True
while is_msg:
    time.sleep(50)
    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        for item in t:
            X = datetime.now()
            X = str(X)
            print(X[:10])
            print(X[11:16])
            print(t[item][0][:10])
            if t[item][0][:10] == X[:10]:
                # if X[11:16] == "15:37":
                connection.sendmail(from_addr=my_email,
                                    to_addrs=t[item][1],
                                    msg=f"Subject:TO Do Task\n\n {item}")
        # is_msg = False
        connection.close()
