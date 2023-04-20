ROOT_DIR = 'resources'
ACTION_DISTRIBUTION = [['1'],  # walk 0
						['1'],  # walk 1
						['12', '13', '14'],  # Climb the wall window interaction 2
						['12', '12', '12'],  # Climb the wall fixed action 3
						['1', '2', '3'],  # Go to the right 4
						['47', '48', '49'],  # Go to the left 5
						['11', '11', '11', '15', '15', '11', '11', '11', '11'],  # Sit still 6
						['15', '16', '17', '16', '17', '15'],  # Tickle7
						['15', '29', '29', '15', '15', '29', '29', '18', '18', '18', '21', '15'],  # Look left and right, make sure no one's on the ground 8
						['15', '11', '15', '11'],  # Nod 9
						['30', '31', '32', '33'],  # Roll upside down 10
						['34', '35', '36', '37'],  # 11
						['38', '39', '40', '41'],  # 12
						['42', '43', '44', '45', '46']]  # 13
PET_ACTIONS_MAP = {'pet_1': ACTION_DISTRIBUTION}
PET_STATUS_MAP = ['standing', 'dragged', 'climb', 'swoop', 'still', 'unmove'];
falling="resources\\falling.mp3"
mew="resources\\mew.mp3"
MUSIC_LIST=[falling,mew]