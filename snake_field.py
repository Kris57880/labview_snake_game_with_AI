def getfield(filed=){
    lis=[0]*(25*35)
    for i in range 25*35 : 
            if filed[i]==6618880:
                lis[i]= 1 # body
            elif field[i]==16711704 :
                lis[i]=2
            else:
                 lis[i]=0
            i += 1
    print(lis)
}