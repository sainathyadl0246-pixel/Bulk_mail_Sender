A = [[7, 0, 0, 0], [1, 0, 1, 0], [0, 1, 1, 0], [4, 0, 0, 6]]
route = [[7], ] # route from 7 is asked.
global flag
temp =-323432 #some random number which is not there in list.
number = int(input("Enter the number you want to reach in list : \n"))  # Enter where you want to check
for i in range(len(A)):
    if temp == number:
        break
    for j in range(len(A[i])):
        if A[i][j] == 1:  #checks if the element is 1 and appends to route
            a=[A[i][j]]
            route.append(a)
            break
        if A[i][j] == number:
            temp=A[i][j]
            a= [temp]
            route.append(a)
            break
flag=False
for i in range(len(A)):
    if number in A[i]:
        flag=True
        break
if flag:
    print(f"The best route from 7 to {number} is {route}")
else:
    print(f"The best route from 7 to {number} is not possible since number not present in any of the lists")