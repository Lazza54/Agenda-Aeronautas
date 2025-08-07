#### VIDEO REFERÊNCIA DESTE CÓDIGO
##  https://www.youtube.com/watch?v=iy3fGZEK8f4&ab_channel=EduardoMendes
#

from pendulum import now, yesterday, tomorrow, timezone
from datetime import datetime
print(now())
print(now('UTC'))

n = now()
y =  yesterday() # yesterday refere-se a zero hora de ontém

print(n.diff(y).in_hours())

##### ----------------------------- UTILIZAR O TIMEZONE AUTOMATICAMENTE

n = now('UTC')
tz1 = timezone('America/Toronto')
tz2 = timezone('America/Sao_Paulo')

print(n) # horário no momento em GMT
print(tz1.convert(n)) # horário no momento em Toronto
print(tz2.convert(n)) # horário no momento em São Paulo
## podemos também resumir
print(n.in_tz('America/Sao_Paulo'))
print(n.in_tz('America/Cuiaba'))

