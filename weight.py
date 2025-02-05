class WeightCalculator:
    def calculate_weight(self, parent_weight, event):
        None

class LinearWeightCalculator(WeightCalculator):
    def calculate_weight(self, parent_weight, event):
        return parent_weight + (event.chance() * event.priority())

class MultiplicationWeightCalculator(WeightCalculator):
    def calculate_weight(self, parent_weight, event):
        return parent_weight + (event.chance() * event.priority())