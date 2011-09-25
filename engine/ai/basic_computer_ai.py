from engine.ai import core_ai

class BasicComputerAI (core_ai.AICore):
    # def __init__(self, *args):
    #     super(BasicComputerAI, self).__init__(*args)
    
    def cycle(self):
        pass


core_ai.register_ai("Basic computer", BasicComputerAI)