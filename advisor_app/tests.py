from django.test import TestCase
from django.urls import reverse
from .models import Schedule, Course, Advisor, Student

# Create your tests here.


class ScheduleModelTests(TestCase):

    # TEST ID 1 #
    def test_empty_schedule(self):
        sched = Schedule(name="test_schedule1", student="test1 test1")
        sched.save()
        self.assertQuerysetEqual(sched.courses.all(), [])
        self.assertEqual(sched.credit, 0)
    # TEST ID 2 #
    def test_add_course_to_empty_schedule(self):
        sched = Schedule(name="test_schedule2", student="test2 test2")
        sched.save()
        test_course = Course(title="test", department="test", section="test",
                             catalog_nbr="0000", credit="3",
                             component="test")
        test_course.save()
        sched.add_course(test_course)
        self.assertQuerysetEqual(sched.courses.all(), [test_course])
        self.assertEqual(sched.credit, 3)
        self.assertEqual(sched.course_creds[str(test_course.id)], 3)
    # TEST ID 3 #
    def test_remove_course_from_empty_schedule(self):
        sched = Schedule(name="test_schedule", student="test test")
        sched.save()
        test_course = Course(title="test", department="test", section="test",
                             catalog_nbr="0000", credit="3",
                             component="test")
        test_course.save()
        sched.remove_course(test_course)
        self.assertQuerysetEqual(sched.courses.all(), [])
        self.assertEqual(sched.credit, 0)
    # TEST ID 4 #
    
    # TEST ID 5 #
    def test_remove_course_from_schedule(self):
        sched = Schedule(name="test_schedule", student="test test")
        sched.save()
        test_course1 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="3",
                              component="test")
        test_course1.save()
        test_course2 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="4",
                              component="test")
        test_course2.save()
        sched.add_course(test_course1)
        sched.add_course(test_course2)
        sched.remove_course(test_course2)
        self.assertQuerysetEqual(sched.courses.all(), [test_course1])
        self.assertEqual(sched.credit, 3)
        self.assertEqual(sched.course_creds[str(test_course1.id)], 3)
        self.assertEqual(sched.course_creds[str(test_course2.id)], 0)
    # TEST ID 6 #
    def test_course_conflict(self):
        sched = Schedule(name="test_schedule", student="test test")
        sched.save()
        test_course1 = Course(title="test", department="test", section="test",
                             catalog_nbr="0000", credit="7", component="test",
                             meetings={"We": [11, 12.25], "Tu": [15, 16.5]})
        test_course1.save()
        test_course2 = Course(title="test", department="test", section="test",
                             catalog_nbr="0000", credit="7", component="test",
                             meetings={"Mo": [11, 12.25], "Tu": [14, 16]})
        test_course2.save()
        sched.add_course(test_course1)
        sched.add_course(test_course2)
        x = sched.validate()
        self.assertEquals(x[2], [[0, 1, 'Tu', [15, 16.5], [14, 16]]])
        self.assertEquals(x[1], "time conflict")
    # TEST ID 7 #
    def test_credit_minimum(self):
        sched = Schedule(name="test_schedule", student="test test")
        sched.save()
        test_course1 = Course(title="test", department="test", section="test",
                             catalog_nbr="0000", credit="3", component="test",
                             meetings={"We": [11, 12.25], "Tu": [15, 16.5]})
        test_course1.save()
        test_course2 = Course(title="test", department="test2", section="test",
                             catalog_nbr="0000", credit="3", component="test",
                             meetings={"Mo": [11, 12.25], "Th": [15, 16.5]})
        test_course2.save()
        sched.add_course(test_course1)
        sched.add_course(test_course2)
        x = sched.validate()
        self.assertEquals(x[1], "credit minimum")
        self.assertEquals(x[2], 6)
    # TEST ID 8 #
    def test_credit_maximum(self):
        sched = Schedule(name="test_schedule", student="test test")
        sched.save()
        test_course1 = Course(title="test", department="test", section="test",
                             catalog_nbr="0000", credit="15", component="test",
                             meetings={"We": [11, 12.25], "Tu": [15, 16.5]})
        test_course2 = Course(title="test", department="test", section="test",
                             catalog_nbr="0000", credit="5", component="test",
                             meetings={"Mo": [11, 12.25], "Th": [14, 16]})
        test_course1.save()
        test_course2.save()
        sched.add_course(test_course1)
        sched.add_course(test_course2)
        x = sched.validate()
        self.assertEquals(x[1], "credit maximum")
        self.assertEquals(x[2], 20)

    # TEST ID 9 #
    def test_change_credits(self):
        sched = Schedule(name="test_schedule", student="test test")
        sched.save()
        test_course1 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="1 - 3",
                              component="test")
        test_course1.save()
        sched.add_course(test_course1)
        sched.change_credits(test_course1, 3)
        x = int(sched.credit)
        sched.change_credits(test_course1, 0)
        self.assertEquals(x-sched.credit, 0) # FIX THIS

class CourseModelTests(TestCase):

    # TEST ID 10 #
    def test_is_ranged(self):
        test_course1 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="1 - 12",
                              component="test")
        test_course1.save()
        self.assertTrue(test_course1.is_ranged())
        test_course2 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="0",
                              component="test")
        test_course2.save()
        self.assertFalse(test_course2.is_ranged())

    # TEST ID 11 #
    def test_max_credits(self):
        test_course1 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="3",
                              component="test")
        test_course1.save()
        self.assertEquals(test_course1.max_credits(), 3)
        test_course2 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="1 - 12",
                              component="test")
        test_course2.save()
        self.assertEquals(test_course2.max_credits(), 12)

    # TEST ID 12 #
    def test_min_credits(self):
        test_course1 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="3",
                              component="test")
        test_course1.save()
        self.assertEquals(test_course1.min_credits(), 3)
        test_course2 = Course(title="test", department="test", section="test",
                              catalog_nbr="0000", credit="7 - 12",
                              component="test")
        test_course2.save()
        self.assertEquals(test_course2.min_credits(), 7)

class AdvisorModelTests(TestCase):

    #TEST ID 13 #
    def test_advisor_add(self):
        advisor = Advisor(name="test_advisor", email="test@advisor.com")
        advisor.save()
        student = Student(name="test_student",email="test@student.com")
        student.save()
        advisor.add_student(student)
        self.assertQuerysetEqual(advisor.students.all(), [student])

    #TEST ID 14 #
    def test_advisor_remove(self):
        student = Student(name="test_student",email="test@student.com")
        student.save()
        advisor = Advisor(name="test_advisor", email="test@advisor.com")
        advisor.save()
        advisor.add_student(student)
        advisor.remove_student(student)
        self.assertQuerysetEqual(advisor.students.all(), [])

