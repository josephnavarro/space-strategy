from text import Text

class Conversation:
    def __init__(self, strings, pos):
        self.pos = pos
        self.dialogue = []
        string_part = []
        count = 0
        for x in range(len(strings)):
            string_part.append(Text(strings[x], scrollable = True))
            count += 1
            if count >= 3 or x == len(strings)-1:
                n = len(string_part)
                for i in range(3-n):
                    string_part.append(Text('', scrollable = True))
                self.dialogue.append(string_part)
                count = 0
                string_part = []
            
        self.read = False
        self.current = 0
        
    def draw(self, surface, pos = (0,0)):
        count = 0
        if len(self.dialogue) > 0:
            for text in self.dialogue[self.current]:
                text.draw(surface, (pos[0],pos[1]+count*16))
                if text.current < len(text.text):
                    break
                else:
                    count += 1
