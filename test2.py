

text = """<tc:textspan start="t_0" end="t_97" type="intervention"/>
<tc:textspan start="t_98" end="t_283" type="intervention"/>
<tc:textspan start="t_284" end="t_341" type="intervention"/>
<tc:textspan start="t_342" end="t_489" type="intervention"/>
<tc:textspan start="t_0" end="t_12" type="paragraph"/>
<tc:textspan start="t_13" end="t_59" type="paragraph"/>
<tc:textspan start="t_60" end="t_81" type="paragraph"/>
<tc:textspan start="t_82" end="t_97" type="paragraph"/>
<tc:textspan start="t_98" end="t_126" type="paragraph"/>
<tc:textspan start="t_127" end="t_159" type="paragraph"/>
<tc:textspan start="t_160" end="t_233" type="paragraph"/>
<tc:textspan start="t_234" end="t_283" type="paragraph"/>
<tc:textspan start="t_284" end="t_341" type="paragraph"/>
<tc:textspan start="t_342" end="t_368" type="paragraph"/>
<tc:textspan start="t_369" end="t_460" type="paragraph"/>
<tc:textspan start="t_461" end="t_467" type="paragraph"/>
<tc:textspan start="t_468" end="t_489" type="paragraph"/>"""


intervention = []
paragraph = []
for i in text.split('\n'):
    end = int(i.split(" ")[2][7:-1])
    atype = i.split(" ")[-1][6:-3]
    globals()[atype].append(end)

# Sanity test.
'''
for i in intervention:
print i
print
for i in paragraph:
print i
'''

paragraph_intervention = []
for i in paragraph:
#     print i, [intervention.index(j) for j in intervention if i <= j] [0]
    for j in intervention:
        if i<=j:
            print paragraph.index(i),intervention.index(j)
            break