from django.db import models

class Course(models.Model):
    title =  models.CharField(max_length=255)
    preview = models.ImageField(upload_to='lms/courses/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preview = models.ImageField(upload_to="lms/lessons/", blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.title
