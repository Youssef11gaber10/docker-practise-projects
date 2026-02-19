from locust import HttpLocust, TaskSet, task


class GetSet(TaskSet):

    @task(10)
    def set_value(l):
        l.client.get('/set?key=name&value=saravanan')

    @task(10)
    def get_value(l):
        l.client.get('/get?key=name')


class User(HttpLocust):
    task_set = GetSet
    min_wait = 0
    max_wait = 5000
