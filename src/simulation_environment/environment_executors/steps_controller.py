class StepsController:
    def __init__(self, steps, social_assets):
        self.step = 0
        self.steps = steps
        self.social_assets = social_assets

    def get_step(self):
        step = self.steps[self.step]
        if step['flood'] is None:
            return {'flood': '', 'victims': [], 'water_samples': [], 'photos': []}

        return step

    def increase_step(self):
        self.step += 1

    def get_steps(self):
        steps = []
        for i in range(self.step):
            if self.steps[i]['flood'] is None or not self.steps[i]['flood'].active:
                continue

            else:
                steps.append(self.steps[i])

    def activate_next_step(self):
        step = self.steps[self.step]
        if step['flood'] is None:
            return

        step['flood'].active = True
        for victim in step['victims']:
            victim.active = True

        for water_sample in step['water_samples']:
            water_sample.active = True

        for photo in step['photos']:
            photo.active = True

    def decrease_period_and_lifetime(self):
        for i in range(self.step):
            if self.steps[i]['flood'] is None:
                continue

            if self.steps[i]['flood'].active:
                self.steps[i]['flood'].period -= 1

                if self.steps[i]['flood'].period == 0:
                    self.steps[i]['flood'].active = False

                    for victim in self.steps[i]['victims']:
                        victim.active = False

                    for water_sample in self.steps[i]['water_samples']:
                        water_sample.active = False

                    for photo in self.steps[i]['photos']:
                        photo.active = False

                else:
                    for victim in self.steps[i]['victims']:
                        if victim.active:
                            victim.lifetime -= 1
                            if victim.lifetime <= 0:
                                victim.active = False
