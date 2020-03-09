from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.models import User
from .forms import *
from .models import Booking, Client
from random import randint
from django import forms
from django.http import JsonResponse
import datetime

# Create your views here.
class BookingView(View):
	template_name = 'booking/bookingform.html'
	def get(self, request):
		user = self.request.user
		bookings = Booking.objects.all()
		startDates = [b.startDate for b in bookings]
		endDates = [b.endDate for b in bookings]
		startTimes = [b.startTime for b in bookings]
		endTimes = [b.endTime for b in bookings]
		allVenues = [b.venue for b in bookings]
		allUsers = [b.attendee for b in bookings]
		allStarts = []
		allEnds = []
		cowCap = Venue.objects.get(name="Coworking Space").cap
		i = 0;
		while i < len(bookings):
			allStarts.append(str(startDates[i]) + ' ' + str(startTimes[i]))
			allEnds.append(str(endDates[i]) + ' ' + str(endTimes[i]))
			i = i + 1
		if user.is_authenticated:
			return render(request = request, template_name = self.template_name, context={'user' : user, 'id': user.username, 'startDates' : allStarts, 'endDates': allEnds, 'venues': allVenues, 'users': allUsers, 'cowCap': cowCap, })
		return redirect('account:Index')

class BookingCalendarView(View):
	form_class = BookingCalendarForm
	template_name = 'booking/bookcal.html'
	def get(self, request):
		form = self.form_class(
			# fr=request.session.get('init_from'), to=request.session.get('init_to'),
			initial= {
			'start_date': request.session.get('init_from'),
			'end_date': request.session.get('init_to'),
			'start_time': datetime.datetime(2020, 12, 12, 9, 30, 0),
			# 'start_time': datetime.datetime(2020, 1, 1, int(request.session.get('init_from_time').split(":")[0]), int(request.session.get('init_from_time').split(":")[1]), 0),
			# 'end_time': datetime.datetime(2020, 1, 1, int(request.session.get('init_to_time').split(":")[0]), int(request.session.get('init_to_time').split(":")[1]), 0),
			})
		refNum = randint(100000, 999999)
		request.session['refNum'] = refNum
		return render(request, template_name=self.template_name, context={'form' : form})
	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			venue = form.cleaned_data['venue']
			venCap = Venue.objects.get(name=venue).cap
			minCap = Venue.objects.get(name=venue).cap
			venComp = Venue.objects.get(name=venue).computers
			minComp = Venue.objects.get(name=venue).computers
			startDays = form.cleaned_data['start_days']
			endDays = form.cleaned_data['end_days']
			startTimes = form.cleaned_data['start_times']
			endTimes = form.cleaned_data['end_times']
			totTimes = 0
			i = 0
			print(str(startDays))
			while i < str(startDays):
				startDate = startDays[i]
				endDate = endDays[i]
				startTime = startTimes[i]
				endTime = endTimes[i]
				i = i + 1
				weekStart = int(startDate.strftime("%w"))
				weekEnd = int(endDate.strftime("%w"))
				if weekEnd < weekStart:
					weekEnd = 6 + weekEnd
				totDays = weekEnd - weekStart + 1
				totTime = (int(endTime.strftime("%H"))-int(startTime.strftime("%H")))
				totMin = (int(endTime.strftime("%M"))-int(startTime.strftime("%M")))
				if totMin == -30:
					totTime -= 0.5
				elif totMin == 30:
					totTime += 0.5
				venBook = Booking.objects.filter(venue=venue)
				bookingLeft = venBook.filter(startDate__lte=startDate).filter(endDate__gte=startDate)
				bookingRight= venBook.filter(endDate__gte=endDate).filter(startDate__lte=endDate)
				bookingMid= venBook.filter(startDate__gte=startDate).filter(endDate__lte=endDate)
				
				conf = bookingRight | bookingLeft | bookingMid
				confLeft = conf.filter(startTime__lte=startTime).filter(endTime__gte=startTime)
				confRight= conf.filter(endTime__gte=endTime).filter(startTime__lte=endTime)
				confMid= conf.filter(startTime__gte=startTime).filter(endTime__lte=endTime)
				finConf = confRight | confLeft | confMid
				print("CONFLICT FOUND ON: " + str(finConf))
				if len(finConf) > 0:
					if venue == 'Coworking Space':
						timeslots = {}
						comps = {}
						for b in finConf:
							start = b.startDate
							end = b.endDate
							stop = False
							while stop == False:
								stTime = b.startTime
								enTime = b.endTime
								while stTime != enTime:
									timesl = str(start) + " " + str(stTime)
									print("Evaluating " + str(stTime))
									exist = timeslots.get(timesl)
									cpExist = comps.get(timesl)
									print(exist)
									if exist == None:
										timeslots[timesl] = len(b.attendee.split(","))
										comps[timesl] = b.computers
									else:
										timeslots[timesl] = exist + len(b.attendee.split(","))
										comps[timesl] = cpExist + b.computers
									print("cap on " + str(timesl) + " is " + str(timeslots[timesl]))
									stTime = (datetime.datetime(2020, 3, 3).combine(start, time(int(stTime.strftime('%H')), int(stTime.strftime('%M')))) + timedelta(minutes=30)).time()
								if str(start) == str(end):
									stop = True
								start = start + timedelta(days=1)
						for timeslot in timeslots:
							if (minCap > venCap-timeslots[timeslot]):
								minCap = venCap-timeslots[timeslot]
							if (minComp > venComp-comps[timeslot]):
								minComp = venComp-comps[timeslot]
			request.session['space'] = minCap
			request.session['comps'] = minComp
			request.session['totDays'] = totDays
			request.session['totTime'] = totTime
			request.session['venue'] = venue
			request.session['startDate'] = str(startDate)
			request.session['endDate'] = str(endDate)
			request.session['startTime'] = str(startTime)
			request.session['endTime'] = str(endTime)
			return redirect('booking:BookingDetails')
		return render(request=request, template_name=self.template_name, context={'form' : form})

class BookingDetailsView(View):
	form_class = BookingDetailsForm
	template_name = 'booking/bookdet.html'
	def get(self, request):
		str_users = []
		user = self.request.user
		form = self.form_class(cap=request.session.get('space'), pcCap=request.session.get('comps'))
		is_cowork = request.session.get('venue') == "Coworking Space"
		if is_cowork == False:
			form.fields['computers'].widget = forms.HiddenInput()
		users = list(Client.objects.all().exclude(first_name=""))
		for u in users:
			str_users.append(str(u) + ' [' + u.username + ']')
		return render(request, self.template_name, context={'form': form, 'users':str_users, 'self': str(user)+' ['+user.username+']', })
	def post(self, request):
		venue = request.session.get('venue')
		venCap = Venue.objects.get(name=venue).cap
		minCap = Venue.objects.get(name=venue).cap
		venComp = Venue.objects.get(name=venue).computers
		minComp = Venue.objects.get(name=venue).computers
		startDays = str(request.session.get('start_days')).split(', ')
		endDays = str(request.session.get('end_days')).split(', ')
		startTimes = str(request.session.get('start_times')).split(', ')
		endTimes = str(request.session.get('end_times')).split(', ')
		totTimes = 0
		i = 0
		last = (len(endTimes)-1)
		endTimes = endTimes[1:len(endTimes)-1]
		endDays = endDays[1:len(endDays)-1]
		startTimes = startTimes[1:len(startTimes)-1]
		startDays = startDays[1:len(startDays)-1]
		while i < len(startDays):
			startDate = startDays[i][1:len(startDays[i])-1]
			endDate = endDays[i][1:len(endDays[i])-1]
			startTime = startTimes[i][1:len(startTimes[i])-1]
			endTime = endTimes[i][1:len(endTimes[i])-1]
			i = i + 1
			# weekStart = int(startDate.strftime("%w"))
			# weekEnd = int(endDate.strftime("%w"))
			# if weekEnd < weekStart:
				# weekEnd = 6 + weekEnd
			totDays = 1
			print(endTime)
			totTime = int(endTime.split(":")[0])-int(startTime.split(":")[1])
			totMin = int(endTime.split(":")[1])-int(startTime.split(":")[1])
			if totMin == -30:
				totTime -= 0.5
			elif totMin == 30:
				totTime += 0.5
			venBook = Booking.objects.filter(venue=venue)
			bookingLeft = venBook.filter(startDate__lte=startDate).filter(endDate__gte=startDate)
			bookingRight= venBook.filter(endDate__gte=endDate).filter(startDate__lte=endDate)
			bookingMid= venBook.filter(startDate__gte=startDate).filter(endDate__lte=endDate)
			
			conf = bookingRight | bookingLeft | bookingMid
			confLeft = conf.filter(startTime__lte=startTime).filter(endTime__gte=startTime)
			confRight= conf.filter(endTime__gte=endTime).filter(startTime__lte=endTime)
			confMid= conf.filter(startTime__gte=startTime).filter(endTime__lte=endTime)
			finConf = confRight | confLeft | confMid
			print("CONFLICT FOUND ON: " + str(finConf))
			if len(finConf) > 0:
				if venue == 'Coworking Space':
					timeslots = {}
					comps = {}
					for b in finConf:
						start = b.startDate
						end = b.endDate
						stop = False
						while stop == False:
							stTime = b.startTime
							enTime = b.endTime
							while stTime != enTime:
								timesl = str(start) + " " + str(stTime)
								print("Evaluating " + str(stTime))
								exist = timeslots.get(timesl)
								cpExist = comps.get(timesl)
								print(exist)
								if exist == None:
									timeslots[timesl] = len(b.attendee.split(","))
									comps[timesl] = b.computers
								else:
									timeslots[timesl] = exist + len(b.attendee.split(","))
									comps[timesl] = cpExist + b.computers
								print("cap on " + str(timesl) + " is " + str(timeslots[timesl]))
								stTime = (datetime.datetime(2020, 3, 3).combine(start, time(int(stTime.strftime('%H')), int(stTime.strftime('%M')))) + timedelta(minutes=30)).time()
							if str(start) == str(end):
								stop = True
							start = start + timedelta(days=1)
					for timeslot in timeslots:
						if (minCap > venCap-timeslots[timeslot]):
							minCap = venCap-timeslots[timeslot]
						if (minComp > venComp-comps[timeslot]):
							minComp = venComp-comps[timeslot]
			request.session['space'] = minCap
			request.session['comps'] = minComp
			request.session['totDays'] = totDays
			request.session['totTime'] = totTime
		attendees = request.POST.get('names')
		attendees_id = request.POST.get('ids')
		print('WARNING! ' + str(len(attendees.split(","))-1))
		form = self.form_class(request.POST, cap=request.session.get('space'), pcCap=request.session.get('comps'), atts=len(attendees.split(","))-1, )
		if form.is_valid():
			attendees = request.POST.get('names')
			attendees_id = request.POST.get('ids')
			purpose = form.cleaned_data['purpose']
			request.session['purpose'] = purpose
			request.session['attendees'] = attendees
			request.session['attendees_id'] = attendees_id
			computers = form.cleaned_data['computers']
			request.session['computers'] = computers
			return redirect('booking:BookingInfo')
		user = request.user
		str_users = []
		users = list(Client.objects.all().exclude(first_name=""))
		for u in users:
			str_users.append(str(u) + ' [' + u.username + ']')
		return render(request, self.template_name, context={'form': form, 'users':str_users, 'self': str(user)+' ['+user.username+']', })

class BookingInfoView(View):
	form_class = BookingInfoForm
	template_name = 'booking/bookcal.html'
	def get(self, request):
		attendees_id = request.session.get('attendees_id')
		cost = request.session.get('totTime') * Venue.objects.get(name=request.session.get('venue')).cost * (len(attendees_id.split(", "))-1) * request.session.get('totDays')
		request.session['cost'] = cost
		form = self.form_class(
			initial={
			'refNum': request.session.get('refNum'), 
			'cost': cost,
			'startDate': request.session.get('startDate'),
			'endDate': request.session.get('endDate'),
			'startTime': request.session.get('startTime'),
			'endTime': request.session.get('endTime'),
			'purpose': request.session.get('purpose'),
			'attendees': request.session.get('attendees'),
			'venue': request.session.get('venue'),
			})
		return render(request, self.template_name, context={'form': form})
	def post(self, request):
		user = self.request.user
		form = self.form_class(request.POST, balance=user.balance, cost=request.session.get('cost'))
		if form.is_valid():
			user.balance = user.balance - request.session.get('cost')
			user.save()
			venue = request.session.get('venue')
			startDate = request.session.get('startDate')
			endDate = request.session.get('endDate')
			startTime = request.session.get('startTime')
			endTime = request.session.get('endTime')
			cost = form.cleaned_data['cost']
			refNum = request.session.get('refNum')
			purpose = request.session.get('purpose')
			attendees_id = request.session.get('attendees_id')
			for at_id in attendees_id.split(", "):
				if at_id.strip() != "":
					booking = Booking(referenceNo=refNum, cost=cost, venue=venue, startTime=startTime, endDate=endDate, startDate=startDate, endTime=endTime, purpose=purpose, attendee=at_id, )
					booking.save()
			print('SUCCESS')
			return redirect('home:Homepage')
		attendees_id = request.session.get('attendees_id')
		cost = request.session.get('totTime') * Venue.objects.get(name=request.session.get('venue')).cost * (len(attendees_id.split(", "))-1) * request.session.get('totDays')
		request.session['cost'] = cost
		form.initial={
			'refNum': request.session.get('refNum'), 
			'cost': cost,
			'startDate': request.session.get('startDate'),
			'endDate': request.session.get('endDate'),
			'startTime': request.session.get('startTime'),
			'endTime': request.session.get('endTime'),
			'purpose': request.session.get('purpose'),
			'attendees': request.session.get('attendees'),
			'venue': request.session.get('venue'),
			}
		return render(request, self.template_name, context={'form': form})

def review_book(request):
	venue = request.GET.get('venue', None)
	fr_day = request.GET.get('from', None)
	fr_to = request.GET.get('to', None)
	print(fr_day + " daysss")
	fr_day = str(fr_day).split(',')
	fr_to = str(fr_to).split(',')
	fr_time = "08:00"
	to_time = "08:00"
	i = 0
	all_day_f = []
	all_day_t = []
	all_time_f = []
	all_time_t = []
	while i < len(fr_day):
		print(i)
		fr_d = fr_day[i]
		fr_t = fr_to[i]
		print(fr_d + " day")
		print(fr_t + " to")
		fr_time = fr_d.split(" ")[1]
		fr_d = fr_d.split(" ")[0]
		to_time = fr_t.split(" ")[1]
		fr_t = fr_t.split(" ")[0]
		all_day_f.append(fr_d)
		all_day_t.append(fr_t)
		all_time_f.append(fr_time)
		all_time_t.append(to_time)
		i = i + 1

	request.session['start_days'] = all_day_f
	request.session['end_days'] = all_day_t
	request.session['start_times'] = all_time_f
	request.session['end_times'] = all_time_t
	request.session['venue'] = venue
	print(all_day_f)
	print(all_day_t)
	print(all_time_f)
	print(all_time_t)
	data = {
		'okay': True,
	}
	return JsonResponse(data)