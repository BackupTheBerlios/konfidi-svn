import Person
import TrustConnection
import TrustSubject
import TrustValue

if __name__ == "__main__":
	t = TrustValue.TrustValue(5)
	print t
	ts1 = TrustSubject.TrustSubject("Default", \
		"http://www.splike.com/ns/trust/subjects/default", t)
	print ts1
	ts2 = TrustSubject.TrustSubject("Email", \
		"http://www.splike.com/ns/trust/subjects/email", TrustValue.TrustValue(9))
	print ts2
	tc1 = TrustConnection.TrustConnection()
	tc1.setFingerprint("dave")
	tc1.addTrustSubject(ts1)
	tc1.addTrustSubject(ts2)
	print tc1
	tc2 = TrustConnection.TrustConnection()
	tc2.setFingerprint("steve")
	tc2.addTrustSubject(ts2)
	tc2.addTrustSubject(ts1)
	print tc2
	p = Person.Person("andy")
	p.addConnection(tc1)
	p.addConnection(tc2)
	print p