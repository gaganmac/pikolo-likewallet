def truncate(num):
	if num > 1000000:
		num = round(num, -6)
		num = str(num)
		num = num[:-6].upper()
		num = num + 'm'
		return num
	elif num > 1000:
		num = round(num, -3)
		num = str(num)
		num = num[:-3].upper()
		num = num + 'k'
		return num
	else:
		return str('{:,}'.format(num))