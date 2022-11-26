import { useState, useEffect } from "react";

function Status({ message, type }) {
  const typeToClass = {
    error: "text-red-800",
    success: "text-green-800",
    info: "text-slate-300",
  };
  return <p className={"text-center p-4 " + typeToClass[type]}>{message}</p>;
}

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

function VideoPlayer({ hidden }) {
  const [shouldRender] = useDelayUnmount(!hidden, 1200, 1200);

  return (
    shouldRender && (
      <div className="w-full transition delay-500 duration-700 ease-in-out">
        <div className="h-40 w-full bg-white"></div>
      </div>
    )
  );
}

export function App() {
  const [status, setStatus] = useState("waiting"); // waiting, error, success

  const handleChange = (event) => {
    const youtubeLink = event.target.value;

    // Check if the link is empty and display waiting status again
    if (youtubeLink.length === 0) {
      setStatus("waiting");
      return;
    }

    // Check if the link is a valid YouTube video link
    if (
      !youtubeLink.match(/^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$/g)
    ) {
      setStatus("error");
      event.target.select();
      return;
    }

    // Otherwise, set the status to success
    setStatus("success");
    event.target.disabled = true;
  };

  return (
    <div className="h-full h-full bg-black text-white min-h-48">
      <div className="max-w-screen-sm mx-auto h-full flex flex-col relative">
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
            <VideoPlayer hidden={status !== "success"} />
          </div>
        </div>
      </div>
    </div>
  );
}
