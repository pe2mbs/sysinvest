from logging import getLogger
from os import getpid, kill
from os.path import split as path_split
import sys
import time
from threading import Thread, RLock, Condition, Lock
from signal import CTRL_BREAK_EVENT, SIGABRT


class WatchdogEvent( object ):
    """Class implementing event objects. based on the threading.Event class
    """
    def __init__(self):
        self._cond = Condition( Lock() )
        self._flag = False
        self._panic = False
        self._run = True
        self._time = time.time()
        return

    def _reset_internal_locks( self ):
        # private!  called by Thread._reset_internal_locks by _after_fork()
        self._cond.__init__( Lock() )
        return

    def is_set( self ):
        """Return true if and only if the internal flag is true."""
        return self._flag

    def set( self ):
        """Set the internal flag to true.

        All threads waiting for it to become true are awakened. Threads
        that call wait() once the flag is true will not block at all.

        """
        with self._cond:
            self._time = time.time()
            self._flag = True
            self._cond.notify_all()

        return

    def stop( self ):
        with self._cond:
            self._run = False
            self._flag = True
            self._cond.notify_all()

        return

    def panic( self ):
        """Set the internal flag to true.

        All threads waiting for it to become true are awakened. Threads
        that call wait() once the flag is true will not block at all.

        """
        with self._cond:
            self._flag = True
            self._time = 0
            self._panic = True
            self._cond.notify_all()

        return

    def is_normal( self ):
        return self._run and not self._panic and self._time > 0

    def is_panic( self ):
        return self._panic

    def checkTimestamp( self, max_diff: int ):
        with self._cond:
            if self._time < time.time() - max_diff:
                self._flag = True
                self._panic = True
                return False

        return True

    @property
    def restTime(self) -> int:
        return int( time.time() - self._time )

    def clear( self ):
        """Reset the internal flag to false.

        Subsequently, threads calling wait() will block until set() is called to
        set the internal flag to true again.

        """
        with self._cond:
            self._flag = False
            self._panic = False
            self._time = time.time()

        return

    def wait( self, timeout = None ):
        """Block until the internal flag is true.

        If the internal flag is true on entry, return immediately. Otherwise,
        block until another thread calls set() to set the flag to true, or until
        the optional timeout occurs.

        When the timeout argument is present and not None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof).

        This method returns the internal flag on exit, so it will always return
        True except if a timeout is given and the operation times out.

        """
        with self._cond:
            signaled = self._flag
            if not signaled:
                signaled = self._cond.wait( timeout )

            return signaled

    def __repr__(self):
        return f"<WdEvent run={self._run} flag={self._flag} panic={self._panic} time={self._time} >"



class ProcessWatchdog( Thread ):
    """
        This class in the process WATCHDOG,

    """
    def __init__( self, timeout = 30 ):
        self.__last_notification = 0
        self.__timeout  = timeout
        self.__event    = WatchdogEvent()
        self.__lock     = RLock()
        self.__pid      = getpid()
        self.__log      = getLogger()
        Thread.__init__( self )
        self.start()
        return

    @property
    def Timeout( self ) -> int:
        return self.__timeout

    def killself( self ):
        if self.__event.is_panic():
            self.__log.critical( "PANIC: Watchdog KILL signal" )
            self.__log.critical( f"PANIC: Killing the whole process by PID: {self.__pid}" )
            kill( self.__pid, SIGABRT )

        return

    def run( self ):
        while not self.__event.is_normal():
            self.__event.wait( self.__timeout )
            if self.__event.is_panic():
                self.__log.critical( f"PANIC: Watchdog give panic state {self.__event}" )

            elif not self.__event.checkTimestamp( self.__timeout ):
                self.__log.critical(f"PANIC: Watchdog timeout expired {self.__event}")

            else:
                self.__log.info( "Watchdog thread alive" )

        self.killself()
        return

    def trigger( self ):
        """
            Function must be called by the thread
        """
        frame = sys._getframe().f_back.f_code   # noqa
        if self.__event.restTime > self.__timeout:
            self.panic()
            return

        self.__log.info( f"Watchdog normal trigger {self.__event.restTime} {path_split(frame.co_filename)[-1]}:{frame.co_name}({frame.co_firstlineno})")
        self.__event.set()
        return

    def panic(self):
        self.__log.info("Watchdog panic trigger")
        self.__event.panic()
        return

    def stop( self ):
        """
            Normal stop of watchdog
        """
        self.__event.stop()
        return