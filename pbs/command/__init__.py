import pbs
import pymake

class Decoder:
    async def parse_function(self, k, args, kwargs, mc=None):

        _ = {
            #'/eval': _eval,
            #'/ReqFile':     pymake.ReqFile,
            #'/ReqDoc':      pymake.req.ReqDoc,
            #'/Array':       functools.partial(coil_testing.array.Array, mc),
            #'/Series':      functools.partial(coil_testing.coil_calc.process.series.Series, mc),
            #'/read_pickle': functools.partial(_read_pickle, mc),
            }

        f = _[k]

        try:

            res = f(*args, **kwargs)

            if asyncio.iscoroutine(res):
                return await res

        except Exception as e:
            logger.error(f'f      = {f!r}')
            logger.error(f'args   = {args!r}')
            logger.error(f'kwargs = {kwargs!r}')
            logger.error(f'e      = {e!r}')
            raise

        return res


async def make(config_file, target=None):
    p = pbs.Project()
    
    p.execfile(config_file)
    
    m = pymake.Makefile()
    
    m.rules += list(p.rules())

    m.decoder = Decoder()

    try:
        if target:
            await m.make(target=target)
        else:
            await m.make(target='all')
    except pymake.BuildError as e:
        print(e)
    except pbs.exception.CompileError as e:
        print(crayons.red(str(e)))


