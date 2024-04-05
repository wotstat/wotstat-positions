
from constants import ROLE_TYPE_TO_LABEL

def shortTankType(tag):
  tags = {
    'lightTank': 'LT',
    'mediumTank': 'MT',
    'heavyTank': 'HT',
    'AT-SPG': 'AT',
    'SPG': 'SPG',
  }
  return tags[tag] if tag in tags else tag


def getTankType(vehicleTags):
  tags = vehicleTags
  res = 'mediumTank' if 'mediumTank' in tags \
    else 'heavyTank' if 'heavyTank' in tags \
    else 'AT-SPG' if 'AT-SPG' in tags \
    else 'SPG' if 'SPG' in tags \
    else 'lightTank' if 'lightTank' in tags \
    else 'None'
  return res

def get_tank_role(role):
  return ROLE_TYPE_TO_LABEL.get(role, 'None')

def mapInterval(value, fromMin, fromMax, toMin, toMax):
  return (value - fromMin) * (toMax - toMin) / (fromMax - fromMin) + toMin