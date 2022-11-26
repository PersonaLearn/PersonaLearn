import { useState, useEffect } from "react";
import ReactPlayer from "react-player";

// ==============================
// > CONSTANTS
// ==============================

const YOUTUBE_VIDEO_REGEX =
  /^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/watch\?v=(.+)$/g;

// ==============================
// > HELPER METHODS
// ==============================

// None yet

// ==============================
// > HOOKS
// ==============================

function useDelayUnmount(isMounted, delayUnmountTime, delayMountTime = 0) {
  const [shouldRender, setShouldRender] = useState(false);

  useEffect(() => {
    let mountTimeoutId;
    let unmountTimeoutId;

    if (isMounted && !shouldRender) {
      mountTimeoutId = setTimeout(() => setShouldRender(true), delayMountTime);
    } else if (!isMounted && shouldRender) {
      unmountTimeoutId = setTimeout(
        () => setShouldRender(false),
        delayUnmountTime
      );
    }

    return () => {
      clearTimeout(unmountTimeoutId);
      clearTimeout(mountTimeoutId);
    };
  }, [isMounted, delayUnmountTime, delayMountTime, shouldRender]);

  return [shouldRender];
}

// ==============================
// > COMPONENTS
// ==============================

function Status({ message, type }) {
  const typeToClass = {
    error: "text-red-800",
    success: "text-green-800",
    info: "text-slate-300",
  };
  return <p className={"text-center p-4 " + typeToClass[type]}>{message}</p>;
}

function YoutubeAcceptor({ onChange, status, hidden }) {
  const [shouldRender] = useDelayUnmount(!hidden, 1200);

  const statusPropsMap = {
    waiting: {
      message: "Paste a YouTube video link above to begin...",
      type: "info",
    },
    error: {
      message: "Please enter a valid YouTube video link.",
      type: "error",
    },
    success: {
      message: "Great! Let's begin.",
      type: "success",
    },
  };

  return (
    shouldRender && (
      <div
        className={`absolute left-0 right-0 transition delay-500 duration-700 ease-in-out ${
          hidden && "opacity-0 translate-y-14"
        }`}
      >
        <input
          className="w-full bg-black border-2 border-gray text-white py-6 mx-6 text-center text-xl placeholder:text-xl placeholder:text-center"
          placeholder="https://youtube.com/watch?v=dQw4w9WgXcQ"
          onChange={onChange}
        />
        <Status {...statusPropsMap[status]} />
      </div>
    )
  );
}

function VideoPlayer({ hidden, link }) {
  const [shouldRender] = useDelayUnmount(!hidden, 1200, 1200);
  const [location, setLocation] = useState(0);
  const [confusingLocations, setConfusingLocations] = useState([]);
  const [playing, setPlaying] = useState(true);

  if (!shouldRender) return null;

  const onProgress = (event) => {
    setLocation(event.playedSeconds);
  };

  const markLocation = () => {
    setConfusingLocations([...confusingLocations, location]);
  };

  const handleFinished = () => {
    setPlaying(false);
  };

  return (
    shouldRender && (
      <div className="w-full transition delay-500 duration-700 ease-in-out px-16">
        <ReactPlayer
          url={link}
          width="100%"
          height="60vh"
          playing={playing}
          style={{ minHeight: "300px" }}
          controls
          onProgress={onProgress}
        />
        <div>
          <div className="p-8 pb-4 flex space-x-8">
            <button
              className="flex-1 px-8 py-4 border-2 border-violet-100 text-violet-100 text-2xl transition hover:-translate-y-1"
              onClick={markLocation}
            >
              Mark Confusing Location
            </button>
            <button
              className="flex-1 px-8 py-4 border-2 border-emerald-100 text-emerald-100 text-2xl transition hover:-translate-y-1"
              onClick={handleFinished}
            >
              I'm Finished →
            </button>
          </div>
          <div className="flex space-x-8">
            <p className="flex-1 text-center text-slate-600">
              {confusingLocations.length} Locations Marked
            </p>
            <div className="flex-1"></div>
          </div>
        </div>
      </div>
    )
  );
}

// ==============================
// > APPLICATION
// ==============================

export function App() {
  const [status, setStatus] = useState("waiting"); // waiting, error, success
  const [youtubeLink, setYoutubeLink] = useState(null);

  const handleChange = (event) => {
    const youtubeLink = event.target.value;

    // Check if the link is empty and display waiting status again
    if (youtubeLink.length === 0) {
      setStatus("waiting");
      return;
    }

    // Check if the link is a valid YouTube video link
    if (!youtubeLink.match(YOUTUBE_VIDEO_REGEX)) {
      setStatus("error");
      event.target.select();
      return;
    }

    // Otherwise, set the status to success
    setStatus("success");
    setYoutubeLink(youtubeLink);
    event.target.disabled = true;
  };

  return (
    <div className="h-full h-full bg-black text-white min-h-48">
      <div className="max-w-screen-lg mx-auto h-full flex flex-col relative">
        <div className="p-16 absolute w-full">
          <h1 className="text-3xl text-center">PersonaLearn Demo</h1>
        </div>
        <div className="flex-1 flex flex-col justify-center">
          <div className="w-full relative">
            <YoutubeAcceptor
              onChange={handleChange}
              status={status}
              hidden={status === "success"}
            />
            <VideoPlayer hidden={status !== "success"} link={youtubeLink} />
          </div>
        </div>
      </div>
    </div>
  );
}
