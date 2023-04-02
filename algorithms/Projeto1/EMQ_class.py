layer = iface.activeLayer()
EMQ = 0
counter = 0

for feature in layer.getFeatures():
    EMQ = EMQ + (feature['erro'])**2
    counter += 1
EMQ = EMQ/counter
EMQ = EMQ**(1/2)
print(f"EMQ = {EMQ}")

A_EP = 1.67
B_EP = 3.33
C_EP = 4.0
D_EP = 5.0

if (EMQ < A_EP):
    print("A classe é a A")

elif (A_EP < EMQ < B_EP):
    print("A classe é a B")
    
elif (B_EP <EMQ < C_EP):
    print("A classe é a C")

elif (C_EP < EMQ < D_EP):
    print("A classe é a D")

else:
    print("Não conforme")