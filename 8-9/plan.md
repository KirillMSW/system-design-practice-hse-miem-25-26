0.
С прошлого занятия:
- Показать как haproxy определяет: мастер это или реплика?
docker exec -it demo-haproxy curl patroni2:8008/replica -iv
docker exec -it demo-haproxy curl patroni2:8008/master -iv

- Read-only replicas

1. etcd - подробнее:
(По очереди)
* Тушим patroni
* Тушим etcd

(Тушим весь etcd)
2025-11-25 13:21:55,527 INFO: demoted self because DCS is not accessible and I was a leader
snapshot etcd
etcdctl snapshot save /home/postgres/snap.db

* Добавить ноду в кластер
- на ходу
* Автоматический failover
* Автоматическое переключение при чтении

Команды:
* Смотрим в кластер: docker exec -it a28e9262e473 patronictl list
* Переключение лидера: docker exec -it a28e9262e473 patronictl switchover --leader patroni2 --candidate patroni3 --force