"""Written by - Rafal Kowalski"""
from flask import request, url_for, redirect

from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater
from flask.ext.admin import expose
from ....models.track import Track
from ....models.event import Event
from ....models.session import Session
from ....models.speaker import Speaker
from ....models import db
from flask import flash
from ....helpers.query_filter import QueryFilter
from open_event.forms.admin.session_form import SessionForm
from open_event.forms.admin.speaker_form import SpeakerForm
from sqlalchemy.orm.collections import InstrumentedList


class EventView(ModelView):

    column_list = ('id',
                   'name',
                   'email',
                   'color',
                   'logo',
                   'start_time',
                   'end_time',
                   'latitude',
                   'longitude',
                   'location_name')

    column_formatters = {
        'name': Formatter.column_formatter,
        'location_name': Formatter.column_formatter,
        'logo': Formatter.column_formatter
    }

    def on_model_change(self, form, model, is_created):
        v = VersionUpdater(event_id=model.id, is_created=is_created, column_to_increment="event_ver")
        v.update()

    @expose('/<event_id>')
    def event(self, event_id):
        events = Event.query.all()
        return self.render('admin/model/track/list1.html', event_id=event_id, events=events)

    @expose('/<event_id>/track')
    def event_tracks(self, event_id):
        tracks = Track.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/track/list1.html', objects=tracks, event_id=event_id, events=events)

    @expose('/<event_id>/track/new', methods=('GET', 'POST'))
    def event_track_new(self, event_id):
        events = Event.query.all()
        from open_event.forms.admin.track_form import TrackForm
        form = TrackForm(request.form)
        if form.validate():
            new_track = Track(name=form.name.data,
                              description=form.description.data,
                              event_id=event_id)
            new_track.session = InstrumentedList([Session.query.get(form.session.data)])
            db.session.add(new_track)
            db.session.commit()
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/track/<track_id>/edit', methods=('GET', 'POST'))
    def event_track_edit(self, event_id, track_id):
        track = Track.query.get(track_id)
        events = Event.query.all()
        from open_event.forms.admin.track_form import TrackForm
        form = TrackForm(obj=track)
        if form.validate():
            track.name = form.name.data
            track.description=form.description.data
            track.session = InstrumentedList([])
            db.session.add(track)
            db.session.commit()
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/track/<track_id>/delete', methods=('GET', 'POST'))
    def event_track_delete(self, event_id, track_id):
        track = Track.query.get(track_id)
        db.session.delete(track)
        db.session.commit()
        flash('You successfully delete track')
        return redirect(url_for('.event_tracks', event_id=event_id))

    @expose('/<event_id>/session')
    def event_sessions(self, event_id):
        sessions = Session.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/session/list.html', objects=sessions, event_id=event_id, events=events)

    @expose('/<event_id>/session/new', methods=('GET', 'POST'))
    def event_session_new(self, event_id):
        events = Event.query.all()
        form = SessionForm()
        if form.validate():
            new_session = Session(title=form.title.data,
                                  subtitle=form.subtitle.data,
                                  description=form.description.data,
                                  start_time=form.start_time.data,
                                  end_time=form.end_time.data,
                                  event_id=event_id,
                                  abstract=form.abstract.data,
                                  type=form.type.data,
                                  level=form.level.data)

            new_session.speakers = InstrumentedList(form.speakers.data if form.speakers.data else [])
            db.session.add(new_session)
            db.session.commit()
            return redirect(url_for('.event_sessions', event_id=event_id))
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/session/<session_id>/edit', methods=('GET', 'POST'))
    def event_session_edit(self, event_id, session_id):
        session = Session.query.get(session_id)
        events = Event.query.all()
        form = SessionForm(obj=session)
        if form.validate():
            session.title = form.title.data
            session.description=form.description.data
            session.subtitle=form.subtitle.data
            session.start_time=form.start_time.data
            session.end_time=form.end_time.data
            session.abstract=form.abstract.data
            session.type=form.type.data
            session.level=form.level.data
            session.speakers = InstrumentedList(form.speakers.data if form.speakers.data else [])
            db.session.add(session)
            db.session.commit()
            return redirect(url_for('.event_sessions', event_id=event_id))
        return self.render('admin/model/session/create.html', form=form, event_id=event_id, events=events)

    @expose('/<event_id>/session/<session_id>/delete', methods=('GET', 'POST'))
    def event_session_delete(self, event_id, session_id):
        session = Session.query.get(session_id)
        db.session.delete(session)
        db.session.commit()
        flash('You successfully delete session')
        return redirect(url_for('.event_sessions', event_id=event_id))

    @expose('/<event_id>/speaker')
    def event_speakers(self, event_id):
        speakers = Speaker.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/speaker/list.html', objects=speakers, event_id=event_id, events=events)

    @expose('/<event_id>/speaker/new', methods=('GET', 'POST'))
    def event_speaker_new(self, event_id):
        events = Event.query.all()
        form = SpeakerForm()
        if form.validate():
            new_speaker = Speaker(name=form.name.data,
                                  photo=form.photo.data,
                                  biography=form.biography.data,
                                  email=form.email.data,
                                  web=form.web.data,
                                  event_id=event_id,
                                  twitter=form.twitter.data,
                                  facebook=form.facebook.data,
                                  github=form.github.data,
                                  linkedin=form.linkedin.data,
                                  organisation=form.organisation.data,
                                  position=form.position.data,
                                  country=form.country.data,
                                  )

            new_speaker.sessions = InstrumentedList(form.sessions.data if form.sessions.data else [])
            db.session.add(new_speaker)
            db.session.commit()
            return redirect(url_for('.event_speakers', event_id=event_id))

        return self.render('admin/model/speaker/create.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/speaker/<speaker_id>/edit', methods=('GET', 'POST'))
    def event_speaker_edit(self, event_id, speaker_id):
        speaker = Speaker.query.get(speaker_id)
        events = Event.query.all()
        form = SpeakerForm(obj=speaker)
        if form.validate():
            speaker.name=form.name.data
            speaker.photo=form.photo.data
            speaker.biography=form.biography.data
            speaker.email=form.email.data
            speaker.web=form.web.data
            speaker.twitter=form.twitter.data
            speaker.facebook=form.facebook.data
            speaker.github=form.github.data
            speaker.linkedin=form.linkedin.data
            speaker.organisation=form.organisation.data
            speaker.position=form.position.data
            speaker.country=form.country.data
            speaker.sessions = InstrumentedList(form.sessions.data if form.sessions.data else [])
            db.session.add(speaker)
            db.session.commit()
            return redirect(url_for('.event_speakers', event_id=event_id))
        return self.render('admin/model/speaker/create.html', form=form, event_id=event_id, events=events)

    @expose('/<event_id>/speaker/<speaker_id>/delete', methods=('GET', 'POST'))
    def event_speaker_delete(self, event_id, speaker_id):
        speaker = Speaker.query.get(speaker_id)
        db.session.delete(speaker)
        db.session.commit()
        flash('You successfully delete speaker')
        return redirect(url_for('.event_speakers', event_id=event_id))